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
const port = 8765;
const debugPort = 9325;
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
    await waitForSelector(cdp, "#analyze-form");

    await submitFixture(cdp, "Atlas Verification Fixture", true);
    const captures = [];
    const checks = {};
    captures.push(await capture(cdp, "desktop-overview.png", ".atlas-header", 1440, 1000));
    captures.push(await capturePanel(cdp, "desktop-astrology.png", "astrology", 1440, 1000));
    captures.push(await capturePanel(cdp, "desktop-bodygraph.png", "human-design", 1440, 1000));
    captures.push(await capturePanel(cdp, "desktop-constellation.png", "constellation", 1440, 1000));
    captures.push(await capture(cdp, "mobile-overview.png", ".atlas-header", 390, 844, true));
    captures.push(await capturePanel(cdp, "mobile-astrology.png", "astrology", 390, 844, true));
    captures.push(await capturePanel(cdp, "mobile-bodygraph.png", "human-design", 390, 844, true));

    checks.sixSurfaces = requireCheck(await evaluate(cdp, "document.querySelectorAll('[data-atlas-panel]').length === 6"), "six Atlas panels");
    checks.uniqueIds = requireCheck(await evaluate(cdp, `(() => { const ids = [...document.querySelectorAll("[id]")].map(node => node.id); return ids.length === new Set(ids).size; })()`), "unique element IDs");
    checks.selectionMatrix = await evaluate(cdp, `(() => {
      const selectors = [".system-node[data-atlas-select]", ".astro-planet", ".bodygraph-center", ".gate-chip.is-active", ".tree-node", ".numerology-row", ".fingerprint-stage"];
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
      calculatedRoot:requireCheck(buttonNames.includes("Calculated identity root"), "accessibility tree exposes constellation root"),
      gate:requireCheck(buttonNames.some(name => name.startsWith("Gate ")), "accessibility tree exposes gates"),
      center:requireCheck(buttonNames.some(name => /^(Head|Ajna|Throat|G\/Identity|Heart\/Ego|Spleen|Sacral|Solar Plexus|Root), /.test(name)), "accessibility tree exposes centers"),
      planet:requireCheck(buttonNames.some(name => / in (Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces) at /.test(name)), "accessibility tree exposes planets"),
    };
    checks.modeSwitch = requireCheck(await evaluate(cdp, `(() => {
      let calls = 0; const original = window.fetch; window.fetch = (...args) => { calls += 1; return original(...args); };
      for (const mode of ["research", "explorer", "research", "explorer"]) app.setAtlasMode(mode);
      window.fetch = original;
      return calls === 0 && document.querySelector(".atlas").dataset.atlasMode === "explorer";
    })()`), "mode changes are presentation-only");
    checks.fullscreenEscape = requireCheck(await evaluate(cdp, `(() => {
      app.toggleAtlasFullscreen("numerology");
      const opened = document.getElementById("atlas-numerology").classList.contains("is-expanded");
      document.dispatchEvent(new KeyboardEvent("keydown", {key:"Escape", bubbles:true}));
      const button = document.querySelector("#atlas-numerology [data-atlas-expand]");
      return opened && !document.getElementById("atlas-numerology").classList.contains("is-expanded") && document.activeElement === button;
    })()`), "fallback fullscreen Escape and focus return");
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
    checks.markdownDownload = requireCheck(downloaded.length === 1 && (await readFile(join(downloadDir, downloaded[0]), "utf8")).startsWith("# Human Metadata Engine Report"), "Markdown download");
    await submitFixture(cdp, "Atlas Verification Fixture", true);
    const firstAtlas = await evaluate(cdp, "document.querySelector('.atlas').innerHTML");
    await submitFixture(cdp, "Atlas Verification Fixture", true);
    const secondAtlas = await evaluate(cdp, "document.querySelector('.atlas').innerHTML");
    checks.repeatedDeterminism = requireCheck(firstAtlas === secondAtlas, "repeated deterministic Atlas DOM");
    await evaluate(cdp, "app.setAtlasMode('research')");
    captures.push(await capture(cdp, "desktop-research.png", ".atlas-header", 1440, 1000));

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
      fixture:{exactBirth:{name:"Atlas Verification Fixture", date:"1985-06-15", time:"10:30", timezone:"America/Chicago", latitude:41.8781, longitude:-87.6298}, nameOnly:{name:"Atlas Name-Only Fixture"}},
      browser:version,
      command:`${process.env.HME_RUN_NETWORK_QA === "1" ? "HME_RUN_NETWORK_QA=1 " : ""}node tools/capture_atlas_baselines.mjs`,
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
