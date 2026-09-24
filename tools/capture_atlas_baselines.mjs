#!/usr/bin/env node

/** Dependency-free Chrome DevTools capture for the sanitized v1.0 Atlas fixture. */

import {createHash} from "node:crypto";
import {existsSync} from "node:fs";
import {mkdir, mkdtemp, readFile, readdir, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {join, resolve} from "node:path";
import {spawn} from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const outputDir = join(root, "docs", "assets", "ui-v10");
const port = Number(process.env.HME_QA_PORT || 8765);
const debugPort = Number(process.env.HME_QA_DEBUG_PORT || 9325);
const baseURL = `http://127.0.0.1:${port}`;
const chromeCandidates = [
  process.env.HME_CHROME_BIN,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "google-chrome",
  "chromium",
].filter(Boolean);
const pythonBinary = process.env.HME_PYTHON_BIN || (existsSync(join(root, ".venv", "bin", "python")) ? join(root, ".venv", "bin", "python") : "python3");

const pause = milliseconds => new Promise(resolvePause => setTimeout(resolvePause, milliseconds));

async function waitFor(url, attempts = 120) {
  let lastError;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return response;
    } catch (error) { lastError = error; }
    await pause(250);
  }
  throw lastError || new Error(`Timed out waiting for ${url}`);
}

class CDP {
  constructor(url) {
    this.nextId = 1;
    this.pending = new Map();
    this.socket = new WebSocket(url);
    this.ready = new Promise((resolveReady, rejectReady) => {
      this.socket.addEventListener("open", resolveReady, {once:true});
      this.socket.addEventListener("error", rejectReady, {once:true});
    });
    this.socket.addEventListener("message", event => {
      const message = JSON.parse(event.data);
      if (!message.id || !this.pending.has(message.id)) return;
      const {resolve: resolveCall, reject} = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolveCall(message.result);
    });
  }

  async send(method, params = {}) {
    await this.ready;
    const id = this.nextId++;
    const response = new Promise((resolveCall, reject) => this.pending.set(id, {resolve:resolveCall, reject}));
    this.socket.send(JSON.stringify({id, method, params}));
    return response;
  }

  close() { this.socket.close(); }
}

async function evaluate(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", {expression, awaitPromise:true, returnByValue:true});
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Browser evaluation failed");
  return result.result.value;
}

async function waitForSelector(cdp, selector) {
  for (let attempt = 0; attempt < 240; attempt += 1) {
    if (await evaluate(cdp, `Boolean(document.querySelector(${JSON.stringify(selector)}))`)) return;
    await pause(250);
  }
  throw new Error(`Timed out waiting for selector: ${selector}`);
}

async function waitForExpression(cdp, expression) {
  for (let attempt = 0; attempt < 240; attempt += 1) {
    if (await evaluate(cdp, expression)) return;
    await pause(250);
  }
  throw new Error(`Timed out waiting for browser expression: ${expression}`);
}

async function viewport(cdp, width, height, mobile = false) {
  await cdp.send("Emulation.setDeviceMetricsOverride", {width, height, deviceScaleFactor:1, mobile});
}

async function capture(cdp, filename, selector, width, height, mobile = false) {
  await viewport(cdp, width, height, mobile);
  const scrollY = await evaluate(cdp, `(() => {
    const element = document.querySelector(${JSON.stringify(selector)});
    document.documentElement.style.scrollBehavior = "auto";
    window.scrollTo(0, Math.max(0, element.getBoundingClientRect().top + window.scrollY - 16));
    return window.scrollY;
  })()`);
  await pause(300);
  const {data} = await cdp.send("Page.captureScreenshot", {format:"png", fromSurface:true, captureBeyondViewport:true, clip:{x:0, y:scrollY, width, height, scale:1}});
  const bytes = Buffer.from(data, "base64");
  await writeFile(join(outputDir, filename), bytes);
  return {file:filename, sha256:createHash("sha256").update(bytes).digest("hex"), width, height, mobile, scrollY};
}

async function capturePanel(cdp, filename, panelId, width, height, mobile = false) {
  await evaluate(cdp, `app.toggleAtlasFullscreen(${JSON.stringify(panelId)})`);
  await waitForSelector(cdp, `#atlas-${panelId}.is-expanded`);
  try {
    return await capture(cdp, filename, `#atlas-${panelId}.is-expanded`, width, height, mobile);
  } finally {
    await evaluate(cdp, `app.toggleAtlasFullscreen(${JSON.stringify(panelId)})`);
  }
}

async function submitReflectionFixture(cdp) {
  await evaluate(cdp, `(() => {
    app.startNew();
    const set = (id, value) => { const element = document.getElementById(id); element.value = value; element.dispatchEvent(new Event("input", {bubbles:true})); };
    set("name", "Atlas Reflection Fixture");
    const enabled = document.getElementById("me-reflection-enabled");
    enabled.checked = true;
    app.toggleMeReflection();
    app.updateMeObservation(0, "text", "Repeatedly documents technical procedures and compares competing explanations before making a decision.");
    app.updateMeObservation(0, "source", "synthetic_qa_fixture");
    app.updateMeObservation(0, "confidence", "high");
    app.toggleMeDomain(0, "crafts_and_technical_practice", true);
    app.toggleMeDomain(0, "knowledge_and_judgment", true);
    document.getElementById("analyze-form").requestSubmit();
  })()`);
  await waitForSelector(cdp, "#dashboard:not([hidden]) .me-reflection-result");
  await evaluate(cdp, `(() => { document.getElementById("dashboard").dataset.atlasMode = "research"; const atlas = document.querySelector(".atlas"); if (atlas) atlas.dataset.atlasMode = "research"; return true; })()`);
  await evaluate(cdp, "document.fonts.ready");
}

async function submitFixture(cdp, name, withBirth) {
  await evaluate(cdp, `(() => {
    app.startNew();
    const set = (id, value) => { const element = document.getElementById(id); element.value = value; element.dispatchEvent(new Event("input", {bubbles:true})); };
    set("name", ${JSON.stringify(name)});
    if (${withBirth}) {
      const enabled = document.getElementById("birth-enabled");
      enabled.checked = true;
      app.toggleSection("birth");
      set("b-date", "1985-06-15");
      set("b-time", "10:30");
      set("b-zone", "America/Chicago");
      set("b-lat", "41.8781");
      set("b-lon", "-87.6298");
    }
    document.getElementById("analyze-form").requestSubmit();
  })()`);
  await waitForSelector(cdp, "#dashboard:not([hidden]) .atlas");
  await evaluate(cdp, "document.fonts.ready");
}

function requireCheck(value, message) {
  if (!value) throw new Error(`Browser verification failed: ${message}`);
  return true;
}

async function main() {
  await mkdir(outputDir, {recursive:true});
  const profileDir = await mkdtemp(join(tmpdir(), "hme-atlas-capture-"));
  const server = spawn(pythonBinary, ["webapp/server.py"], {cwd:root, env:{...process.env, PORT:String(port)}, stdio:["ignore", "pipe", "pipe"]});
  let chrome;
  try {
    await waitFor(`${baseURL}/readyz`);
    const chromeBinary = chromeCandidates[0];
    if (!chromeBinary) throw new Error("Set HME_CHROME_BIN to a Chrome executable");
    chrome = spawn(chromeBinary, [
      "--headless=new", `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profileDir}`,
      "--no-first-run", "--disable-background-networking", "--hide-scrollbars", baseURL,
    ], {stdio:"ignore"});
    await waitFor(`http://127.0.0.1:${debugPort}/json/list`);
    const targets = await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json();
    const page = targets.find(target => target.type === "page");
    if (!page) throw new Error("Chrome did not expose a page target");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Emulation.setFocusEmulationEnabled", {enabled:true});
    await waitForSelector(cdp, "#analyze-form");

    const captures = [];
    const checks = {};
    captures.push(await capture(cdp, "desktop-first-run.png", "#landing", 1440, 1000));
    captures.push(await capture(cdp, "mobile-first-run.png", "#landing", 390, 844, true));
    captures.push(await capture(cdp, "mobile-privacy-before-input.png", "#privacy-before-input", 390, 844, true));
    checks.firstRunNoHorizontalOverflow = {};
    for (const width of [320, 360, 390, 412, 768]) {
      await viewport(cdp, width, 844, true);
      checks.firstRunNoHorizontalOverflow[width] = requireCheck(
        await evaluate(cdp, "document.documentElement.scrollWidth <= document.documentElement.clientWidth"),
        `first-run no horizontal overflow at ${width}px`,
      );
    }
    checks.firstRunTrustOrder = requireCheck(await evaluate(cdp, `(() => {
      const trust = document.getElementById("privacy-before-input");
      const name = document.getElementById("name");
      return Boolean(trust && name && (trust.compareDocumentPosition(name) & Node.DOCUMENT_POSITION_FOLLOWING));
    })()`), "privacy disclosure precedes first PII field");
    checks.publicIdentity = requireCheck(await evaluate(cdp, `document.title.includes("The Human Manual") && document.body.textContent.includes("Inversion Labs") && document.body.textContent.includes("Your information is an input, not the product.")`), "Human Manual identity and trust statement");
    await viewport(cdp, 1440, 1000, false);

    await submitFixture(cdp, "Atlas Verification Fixture", true);
    captures.push(await capture(cdp, "desktop-overview.png", ".atlas-header", 1440, 1000));
    captures.push(await capturePanel(cdp, "desktop-astrology.png", "astrology", 1440, 1000));
    captures.push(await capturePanel(cdp, "desktop-bodygraph.png", "human-design", 1440, 1000));
    captures.push(await capturePanel(cdp, "desktop-constellation.png", "constellation", 1440, 1000));
    captures.push(await capture(cdp, "mobile-overview.png", ".atlas-header", 390, 844, true));
    captures.push(await capturePanel(cdp, "mobile-astrology.png", "astrology", 390, 844, true));
    captures.push(await capturePanel(cdp, "mobile-bodygraph.png", "human-design", 390, 844, true));

    checks.protectedSixSurfaces = requireCheck(await evaluate(cdp, `(() => {
      const required = ["constellation","astrology","human-design","tree-of-life","numerology","fingerprint"];
      return required.every(id => document.getElementById("atlas-" + id));
    })()`), "protected six Atlas panels");
    checks.expandedSurfaceCount = requireCheck(await evaluate(cdp, "document.querySelectorAll('[data-atlas-panel]').length >= 14"), "expanded Atlas panel count");
    const duplicateIds = await evaluate(cdp, `(() => { const ids = [...document.querySelectorAll("[id]")].map(node => node.id); return [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))]; })()`);
    checks.uniqueIds = requireCheck(duplicateIds.length === 0, "unique element IDs: " + duplicateIds.join(", "));
    checks.selectionMatrix = await evaluate(cdp, `(() => {
      const selectors = [
        ".system-node[data-atlas-select]", ".astro-planet", ".bodygraph-center", ".gate-chip.is-active",
        ".tree-node", ".numerology-row", ".fingerprint-stage", ".exp-wheel-body", ".bazi-pillar",
        ".maya-count-cell", ".visual-lab-card .lab-card-select", ".visual-lab-card--boundary .lab-card-select", ".evidence-layer-row"
      ];
      return selectors.map(selector => {
        const element = document.querySelector(selector);
        if (!element) return {selector, ok:false};
        element.dispatchEvent(new MouseEvent("click", {bubbles:true}));
        return {selector, ok:Boolean(document.querySelector("#atlas-inspector-content h3")), selected:document.querySelectorAll(".is-selected").length};
      });
    })()`);
    requireCheck(checks.selectionMatrix.every(row => row.ok && row.selected >= 1), "selection on every surface");
    await cdp.send("Accessibility.enable");
    const accessibility = await cdp.send("Accessibility.getFullAXTree");
    const buttonNames = accessibility.nodes.filter(node => node.role?.value === "button").map(node => node.name?.value || "");
    checks.accessibilityTree = {
      namedButtons:buttonNames.filter(Boolean).length,
      calculatedRoot:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.system-node--identity[role="button"][tabindex="0"][aria-label="Calculated identity root"]'))`), "constellation root exposes keyboard button semantics"),
      gate:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.gate-chip.is-active')) && document.querySelector('.gate-chip.is-active').tagName === "BUTTON"`), "active gate uses a native button"),
      center:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.bodygraph-center[role="button"][tabindex="0"][aria-label]'))`), "bodygraph center exposes keyboard button semantics"),
      planet:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.astro-planet[role="button"][tabindex="0"][aria-label]'))`), "astrology planet exposes keyboard button semantics"),
      jyotish:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.exp-wheel-body[role="button"][tabindex="0"][aria-label]'))`), "Jyotish body exposes keyboard button semantics"),
      bazi:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.bazi-pillar')) && document.querySelector('.bazi-pillar').tagName === "BUTTON"`), "BaZi pillar uses a native button"),
      maya:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.maya-count-cell')) && document.querySelector('.maya-count-cell').tagName === "BUTTON"`), "Maya Long Count cell uses a native button"),
      lab:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.visual-lab-card .lab-card-select')) && document.querySelector('.visual-lab-card .lab-card-select').tagName === "BUTTON"`), "visual-lab record uses a native button"),
      evidence:requireCheck(await evaluate(cdp, `Boolean(document.querySelector('.evidence-layer-row')) && document.querySelector('.evidence-layer-row').tagName === "BUTTON"`), "evidence layer uses a native button"),
    };
    checks.modeSwitch = requireCheck(await evaluate(cdp, `(() => {
      let calls = 0; const original = window.fetch; window.fetch = (...args) => { calls += 1; return original(...args); };
      for (const mode of ["research", "explorer", "research", "explorer"]) app.setAtlasMode(mode);
      window.fetch = original;
      return calls === 0 && document.querySelector(".atlas").dataset.atlasMode === "explorer";
    })()`), "mode changes are presentation-only");
    checks.storyMode = requireCheck(await evaluate(cdp, `(() => {
      let calls = 0; const original = window.fetch; window.fetch = (...args) => { calls += 1; return original(...args); };
      app.setNarrativeMode("mythic");
      const storyPanel = document.querySelector('[data-narrative-panel="mythic"]');
      const storyButton = [...document.querySelectorAll('[data-narrative-mode]')].find(button => button.textContent.trim() === "Story");
      const groundedButton = [...document.querySelectorAll('[data-narrative-mode]')].find(button => button.textContent.trim() === "Grounded");
      const sourcesButton = [...document.querySelectorAll('[data-narrative-mode]')].find(button => button.textContent.trim() === "Sources");
      const ok = calls === 0 && storyPanel && !storyPanel.hidden && storyButton?.getAttribute("aria-pressed") === "true" && groundedButton && sourcesButton && storyPanel.textContent.trim().length > 500;
      window.fetch = original;
      return Boolean(ok);
    })()`), "Story mode is local, deterministic, labeled, and substantial");
    checks.agentHandoffPrompt = requireCheck(await evaluate(cdp, `(() => {
      const prompt = document.querySelector(".agent-handoff-prompt");
      const text = prompt?.textContent || "";
      return Boolean(prompt && text.includes("cool fucking story") && text.includes("favorite agent") && text.includes("Welcome to the Inversion"));
    })()`), "post-report bring-your-own-agent handoff prompt");
    const fallbackOpened = await evaluate(cdp, `(() => {
      const panel = document.getElementById("atlas-numerology");
      const button = panel.querySelector("[data-atlas-expand]");
      button.dataset.hmeFocusCalls = "0";
      button.__hmeOriginalFocus = button.focus.bind(button);
      button.focus = (...args) => {
        button.dataset.hmeFocusCalls = String(Number(button.dataset.hmeFocusCalls || "0") + 1);
        return button.__hmeOriginalFocus(...args);
      };
      try { Object.defineProperty(panel, "requestFullscreen", {value: undefined, configurable: true}); } catch (_) {}
      app.toggleAtlasFullscreen("numerology");
      return panel.classList.contains("is-expanded");
    })()`);
    await cdp.send("Input.dispatchKeyEvent", {type:"keyDown", key:"Escape", code:"Escape", windowsVirtualKeyCode:27, nativeVirtualKeyCode:27});
    await cdp.send("Input.dispatchKeyEvent", {type:"keyUp", key:"Escape", code:"Escape", windowsVirtualKeyCode:27, nativeVirtualKeyCode:27});
    await pause(50);
    const fallbackClosedAndRestored = await evaluate(cdp, `(() => {
      const panel = document.getElementById("atlas-numerology");
      const button = panel.querySelector("[data-atlas-expand]");
      const focusCalls = Number(button.dataset.hmeFocusCalls || "0");
      const focusable = !button.disabled && button.tabIndex >= 0 && getComputedStyle(button).display !== "none" && getComputedStyle(button).visibility !== "hidden";
      const ok = !panel.classList.contains("is-expanded") && focusCalls >= 1 && focusable;
      if (button.__hmeOriginalFocus) button.focus = button.__hmeOriginalFocus;
      delete button.__hmeOriginalFocus;
      delete button.dataset.hmeFocusCalls;
      try { delete panel.requestFullscreen; } catch (_) {}
      return ok;
    })()`);
    checks.fullscreenEscape = requireCheck(fallbackOpened && fallbackClosedAndRestored, "fallback fullscreen Escape closes and requests focus restoration");
    checks.noHorizontalOverflow = {};
    for (const width of [320, 360, 390, 412, 768]) {
      await viewport(cdp, width, 844, true);
      checks.noHorizontalOverflow[width] = requireCheck(await evaluate(cdp, "document.documentElement.scrollWidth <= document.documentElement.clientWidth"), `no horizontal overflow at ${width}px`);
    }
    await viewport(cdp, 1440, 1000, false);
    await cdp.send("Emulation.setEmulatedMedia", {media:"print"});
    checks.print = requireCheck(await evaluate(cdp, `(() => {
      const shown = element => getComputedStyle(element).display !== "none";
      return shown(document.querySelector(".gate-grid")) && shown(document.querySelector(".atlas-text-equivalent")) && !shown(document.querySelector(".atlas-inspector"));
    })()`), "print preserves gate data and text provenance");
    await cdp.send("Emulation.setEmulatedMedia", {media:"screen"});
    checks.printAction = requireCheck(await evaluate(cdp, `(() => {
      window.__hmePrintCalled = false; window.print = () => { window.__hmePrintCalled = true; };
      document.querySelector('.atlas-header-actions [onclick="window.print()"]')?.click();
      return window.__hmePrintCalled;
    })()`), "print action");
    const downloadDir = join(profileDir, "downloads");
    await mkdir(downloadDir, {recursive:true});
    await cdp.send("Browser.setDownloadBehavior", {behavior:"allow", downloadPath:downloadDir, eventsEnabled:true});
    await evaluate(cdp, "app.downloadReport()");
    let downloaded = [];
    for (let attempt = 0; attempt < 40; attempt += 1) {
      downloaded = (await readdir(downloadDir)).filter(name => name.endsWith(".md"));
      if (downloaded.length) break;
      await pause(100);
    }
    const downloadedMarkdown = downloaded.length === 1 ? await readFile(join(downloadDir, downloaded[0]), "utf8") : "";
    checks.markdownDownload = requireCheck(
      downloaded.length === 1 &&
      downloadedMarkdown.startsWith("# The Human Manual Report") &&
      downloadedMarkdown.includes("## Agent Handoff") &&
      downloadedMarkdown.includes("Do not invent missing personal facts") &&
      downloadedMarkdown.includes("Preserve contradictions"),
      "Human Manual Markdown download with Agent Handoff",
    );
    await submitFixture(cdp, "Atlas Verification Fixture", true);
    const firstAtlas = await evaluate(cdp, "document.querySelector('.atlas').innerHTML");
    await submitFixture(cdp, "Atlas Verification Fixture", true);
    const secondAtlas = await evaluate(cdp, "document.querySelector('.atlas').innerHTML");
    checks.repeatedDeterminism = requireCheck(firstAtlas === secondAtlas, "repeated deterministic Atlas DOM");
    await evaluate(cdp, "app.setAtlasMode('research')");
    captures.push(await capture(cdp, "desktop-research.png", ".atlas-header", 1440, 1000));

    await submitReflectionFixture(cdp);
    captures.push(await capture(cdp, "desktop-sumerian-reflection.png", ".me-reflection-result", 1440, 1000));
    captures.push(await capture(cdp, "mobile-sumerian-reflection.png", ".me-reflection-result", 390, 844, true));
    checks.sumerianReflection = await evaluate(cdp, `(() => {
      const labels = [...document.querySelectorAll(".me-epistemic-chain strong")].map(node => node.textContent.trim());
      const matches = [...document.querySelectorAll(".me-match")];
      if (matches[0]) matches[0].open = true;
      const matchLabels = matches.map(node => node.querySelector("summary strong")?.textContent.trim() || "").sort();
      return {
        labels, matchCount:matches.length, matchLabels,
        expandedText:matches[0]?.textContent || "",
        boundaryText:document.querySelector(".me-reflection-result .limits-note")?.textContent || "",
      };
    })()`);
    requireCheck(JSON.stringify(checks.sumerianReflection.labels) === JSON.stringify(["Personal evidence","Modern analytical bridge","Historical corpus"]), "three-layer labels");
    requireCheck(checks.sumerianReflection.matchCount === 2, "two expandable reflection matches");
    requireCheck(checks.sumerianReflection.matchLabels.some(label => label.includes("Crafts")) && checks.sumerianReflection.matchLabels.some(label => label.includes("Knowledge")), "exact tagged reflection categories rendered");
    requireCheck(checks.sumerianReflection.expandedText.includes("Modern capacity crosswalk") && checks.sumerianReflection.expandedText.includes("Historical corpus items grouped here"), "expanded modern/historical separation");
    requireCheck(checks.sumerianReflection.boundaryText.includes("not evidence that the Sumerians assigned"), "historical-personal boundary copy");
    checks.sumerianReflection.mobileNoOverflow = requireCheck(await evaluate(cdp, "document.documentElement.scrollWidth <= document.documentElement.clientWidth"), "reflection no horizontal overflow at 390px");
    await viewport(cdp, 1440, 1000, false);

    await submitFixture(cdp, "Atlas Name-Only Fixture", false);
    captures.push(await capturePanel(cdp, "desktop-unavailable-name-only.png", "astrology", 1440, 1000));
    checks.unavailableReplacement = requireCheck(await evaluate(cdp, `!document.querySelector(".astro-planet") && !document.querySelector(".bodygraph-center") && document.querySelectorAll(".atlas-unavailable").length >= 2`), "name-only result replaces exact-birth graphics");
    await evaluate(cdp, `(() => {
      app.startNew();
      const set = (id, value) => { const element = document.getElementById(id); element.value = value; element.dispatchEvent(new Event("input", {bubbles:true})); };
      set("name", "Atlas Unknown-Time Fixture");
      document.getElementById("birth-enabled").checked = true; app.toggleSection("birth");
      set("b-date", "1985-06-15");
      document.getElementById("b-time-unknown").checked = true; app.toggleUnknownTime();
      set("b-zone", "America/Chicago"); set("b-lat", "41.8781"); set("b-lon", "-87.6298");
      document.getElementById("analyze-form").requestSubmit();
    })()`);
    await waitForSelector(cdp, "#dashboard:not([hidden]) .atlas");
    checks.unknownTime = requireCheck(await evaluate(cdp, `Boolean(document.querySelector("#atlas-astrology svg")) && Boolean(document.querySelector("#atlas-human-design .atlas-unavailable")) && [...document.querySelectorAll(".atlas-summary strong")].some(node => node.textContent === "Date only")`), "unknown-time withholding");
    checks.startNewHidesCharts = requireCheck(await evaluate(cdp, `(() => { app.startNew(); return document.getElementById("dashboard").hidden; })()`), "start-new hides prior charts");
    await evaluate(cdp, `(() => { document.getElementById("name").value = "<img src=x onerror=alert(1)>"; document.getElementById("analyze-form").requestSubmit(); })()`);
    await waitForSelector(cdp, "#form-error-summary:not([hidden])");
    checks.hostileName = requireCheck(await evaluate(cdp, `document.getElementById("dashboard").hidden && document.getElementById("form-error").textContent.length > 0 && !document.querySelector("#form-error img")`), "hostile name is rejected without HTML insertion");
    if (process.env.HME_RUN_NETWORK_QA === "1") {
      await evaluate(cdp, `(() => {
        app.startNew();
        const set = (id, value) => { const element = document.getElementById(id); element.value = value; element.dispatchEvent(new Event("input", {bubbles:true})); };
        set("name", "Atlas Ambiguous-Location Fixture");
        document.getElementById("birth-enabled").checked = true; app.toggleSection("birth");
        set("b-date", "1985-06-15"); document.getElementById("b-time-unknown").checked = true; app.toggleUnknownTime();
        set("b-loc", "Springfield"); document.getElementById("analyze-form").requestSubmit();
      })()`);
      await waitForExpression(cdp, `!document.getElementById("location-choices").hidden || !document.getElementById("form-error-summary").hidden`);
      checks.ambiguousLocation = requireCheck(await evaluate(cdp, `!document.getElementById("location-choices").hidden && document.querySelectorAll(".location-choice").length > 1`), "live ambiguous-location choices");
    }
    const version = await evaluate(cdp, "navigator.userAgent");
    const manifest = {
      fixture:{exactBirth:{name:"Atlas Verification Fixture", date:"1985-06-15", time:"10:30", timezone:"America/Chicago", latitude:41.8781, longitude:-87.6298}, nameOnly:{name:"Atlas Name-Only Fixture"}, reflection:{name:"Atlas Reflection Fixture", observation:"Synthetic QA observation", capacityDomains:["crafts_and_technical_practice","knowledge_and_judgment"]}},
      browser:version,
      command:`${process.env.HME_RUN_NETWORK_QA === "1" ? "HME_RUN_NETWORK_QA=1 " : ""}${process.env.HME_QA_PORT ? `HME_QA_PORT=${port} ` : ""}${process.env.HME_QA_DEBUG_PORT ? `HME_QA_DEBUG_PORT=${debugPort} ` : ""}node tools/capture_atlas_baselines.mjs`,
      captures,
      checks,
    };
    await writeFile(join(outputDir, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
    cdp.close();
    process.stdout.write(`${JSON.stringify(manifest, null, 2)}\n`);
  } finally {
    chrome?.kill("SIGTERM");
    server.kill("SIGTERM");
    await rm(profileDir, {recursive:true, force:true});
  }
}

main().catch(error => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
