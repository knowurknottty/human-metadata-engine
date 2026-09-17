/* Tarot is independent of identity analysis. Intentions never leave this page. */
(() => {
  "use strict";
  const root = document.getElementById("tarot-reading");
  if (!root) return;
  const form = root.querySelector("form");
  const submit = root.querySelector("[data-tarot-draw]");
  const status = root.querySelector("[data-tarot-status]");
  const result = root.querySelector("[data-tarot-result]");
  const save = root.querySelector("[data-tarot-save]");
  let reading = null;
  let readingIntention = "";
  let pending = false;
  const element = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (pending) return;
    const spread = new FormData(form).get("spread");
    const intention = root.querySelector("textarea").value.trim();
    pending = true;
    submit.disabled = true;
    status.textContent = "Shuffling the deck…";
    root.setAttribute("aria-busy", "true");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch("/api/tarot", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({spread}), signal: controller.signal,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || data.error || "The draw could not be completed.");
      const counts = {focus: 1, situation: 3, crossroads: 5};
      if (data.schema_version !== "tarot-reading-v1" || data.spread !== spread || !Array.isArray(data.cards) || data.cards.length !== counts[spread] || new Set(data.cards.map(c => c.id)).size !== data.cards.length || !data.cards.every(c => Array.isArray(c.paragraphs) && c.paragraphs.every(p => typeof p === "string"))) throw new Error("The server returned an incomplete reading. Your previous reading has been kept.");
      const fragment = document.createDocumentFragment();
      const heading = element("h3", data.title);
      heading.tabIndex = -1;
      fragment.append(heading);
      if (intention) fragment.append(element("p", `Your question: ${intention}`, "tarot-intention"));
      const spreadStage = element("div", undefined, "tarot-spread-stage");
      spreadStage.dataset.spread = spread;
      spreadStage.setAttribute("aria-label", `${data.title} card layout`);
      const interpretations = element("div", undefined, "tarot-interpretations");
      interpretations.dataset.spread = spread;
      data.cards.forEach((card, index) => {
        const visual = element("article", undefined, "tarot-card-visual");
        visual.dataset.position = String(index + 1);
        const face = element("div", undefined, "tarot-card-face");
        face.append(element("span", `${index + 1} · ${card.position}`, "tarot-position"));
        const mark = element("span", card.arcana === "Major" ? "✧" : ({Wands:"✶", Cups:"◡", Swords:"◇", Pentacles:"✥"}[card.suit] || "✧"), "tarot-card-mark");
        mark.setAttribute("aria-hidden", "true");
        face.append(mark, element("span", card.name, "tarot-card-name"), element("small", `${card.arcana} arcana · Upright`));
        visual.append(face);
        spreadStage.append(visual);

        const article = element("article", undefined, "tarot-card-reading");
        article.append(element("p", `${index + 1} · ${card.position}`, "tarot-reading-position"));
        article.append(element("h4", card.name), element("p", card.question, "tarot-card-question"));
        const details = element("details");
        details.open = index === 0 || spread === "focus";
        details.append(element("summary", "Read this card"));
        card.paragraphs.forEach(text => details.append(element("p", text)));
        article.append(details);
        interpretations.append(article);
      });
      fragment.append(spreadStage, element("h3", "Read the cards"), interpretations, element("h3", "Read the spread together"), element("p", data.synthesis));
      const method = element("details", undefined, "tarot-method");
      method.append(element("summary", "How this reading was made"), element("p", data.method), element("p", data.interpretation), element("p", `Reading ${data.reading_id} · ${data.schema_version}`));
      fragment.append(method, element("p", data.disclaimer, "field-hint"));
      result.replaceChildren(fragment);
      reading = data;
      readingIntention = intention;
      save.hidden = false;
      submit.textContent = "Shuffle and draw a new reading";
      status.textContent = `${data.cards.length} ${data.cards.length === 1 ? "card" : "cards"} drawn. No AI used. Your reading stays here until you draw again or leave the page.`;
      heading.focus();
    } catch (error) {
      status.textContent = error.name === "AbortError" ? "The draw timed out. Try again when the connection returns; any previous reading remains below." : (error.message || "Unable to draw. Please try again.");
    } finally {
      clearTimeout(timeout);
      pending = false;
      submit.disabled = false;
      root.removeAttribute("aria-busy");
    }
  });
  save.addEventListener("click", () => {
    if (!reading) return;
    const lines = [`# ${reading.title}`, "", reading.disclaimer, ""];
    if (readingIntention) lines.push(`Your question: ${readingIntention}`, "");
    for (const card of reading.cards) lines.push(`## ${card.position}: ${card.name}`, "", card.question, "", ...card.paragraphs.flatMap(p => [p, ""]));
    lines.push("## Read the spread together", "", reading.synthesis, "", "## Method", "", reading.method, "", reading.interpretation, "", `Reading: ${reading.reading_id}`, `Version: ${reading.schema_version}`, `Spread: ${reading.spread}`, `Card IDs: ${reading.cards.map(c => c.id).join(", ")}`);
    const url = URL.createObjectURL(new Blob([lines.join("\n")], {type:"text/markdown;charset=utf-8"}));
    const link = element("a"); link.href = url; link.download = `tarot-${reading.reading_id}.md`;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
})();
