"use strict";

(() => {
  const search = document.querySelector("#search");
  const filters = document.querySelector("#filters");
  const grid = document.querySelector("#pack-grid");
  const status = document.querySelector("#results-status");
  const error = document.querySelector("#load-error");
  const empty = document.querySelector("#empty-state");
  const selection = { industry: "", function: "" };
  let packs = [];

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function link(text, url, className, accessibleLabel) {
    const node = element("a", className, text);
    node.href = url;
    if (accessibleLabel) node.setAttribute("aria-label", accessibleLabel);
    return node;
  }

  function safeUrl(value, optional = false) {
    if (optional && value === "") return true;
    if (typeof value !== "string") return false;
    try {
      const url = new URL(value);
      return url.protocol === "https:" && !url.username && !url.password;
    } catch {
      return false;
    }
  }

  function validateCatalog(data) {
    if (!Array.isArray(data)) throw new Error("Catalog must be an array.");
    const ids = new Set();
    const requiredText = ["id", "title", "summary", "industry", "function", "author", "updated"];
    for (const pack of data) {
      if (!pack || requiredText.some(key => typeof pack[key] !== "string" || !pack[key].trim())) {
        throw new Error("Missing required pack metadata.");
      }
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(pack.id) || ids.has(pack.id)) throw new Error("Invalid or duplicate pack ID.");
      if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(pack.updated)) throw new Error("Invalid review month.");
      if (!Array.isArray(pack.features) || !pack.features.length || pack.features.some(tag => typeof tag !== "string" || !tag.trim())) throw new Error("Invalid feature tags.");
      if (pack.tags !== undefined && (!Array.isArray(pack.tags) || pack.tags.some(tag => typeof tag !== "string"))) throw new Error("Invalid search tags.");
      if (!safeUrl(pack.pagesUrl) || !safeUrl(pack.repoUrl) || !safeUrl(pack.demoUrl, true)) throw new Error("Pack links must be HTTPS.");
      if (pack.access !== undefined && !["public", "internal"].includes(pack.access)) throw new Error("Invalid access label.");
      ids.add(pack.id);
    }
    return data;
  }

  function buildFilters() {
    filters.replaceChildren();
    for (const [key, label] of [["industry", "Industry"], ["function", "Function"]]) {
      const group = element("fieldset");
      group.append(element("legend", "", label));
      const choices = [...new Set(packs.map(pack => pack[key]))].sort();
      const chips = element("div", "chips");
      for (const value of ["", ...choices]) {
        const button = element("button", "chip", value || "All");
        button.type = "button";
        button.dataset.filter = key;
        button.dataset.value = value;
        button.setAttribute("aria-pressed", String(selection[key] === value));
        button.addEventListener("click", () => {
          selection[key] = value;
          updateChips();
          render();
        });
        chips.append(button);
      }
      group.append(chips);
      filters.append(group);
    }
  }

  function updateChips() {
    filters.querySelectorAll("button").forEach(button => {
      button.setAttribute("aria-pressed", String(selection[button.dataset.filter] === button.dataset.value));
    });
  }

  function packCard(pack) {
    const internal = pack.access === "internal";
    const card = element("article", "pack-card");
    card.dataset.packId = pack.id;
    const headingId = `pack-${pack.id}`;
    card.setAttribute("aria-labelledby", headingId);
    const badges = element("div", "card-top");
    badges.append(element("span", "badge", pack.industry), element("span", "badge function-badge", pack.function));
    const heading = element("h3", "", pack.title);
    heading.id = headingId;
    card.append(badges, heading, element("p", "pack-summary", pack.summary));
    if (internal) card.append(element("p", "access-note", "Internal · Snowflake employees only"));
    const features = element("ul", "feature-tags");
    features.setAttribute("aria-label", "Snowflake features and capabilities");
    pack.features.forEach(feature => features.append(element("li", "", feature)));
    card.append(features);
    const meta = element("div", "pack-meta");
    const updated = element("time", "", `Reviewed ${pack.updated}`);
    updated.dateTime = pack.updated;
    meta.append(updated);
    card.append(meta);
    const actions = element("div", "card-actions");
    const accessLabel = internal ? "; employee sign-in required" : "";
    actions.append(link("View pack ↗", pack.pagesUrl, "button primary", `View ${pack.title}${accessLabel}`));
    if (pack.demoUrl) actions.append(link("Try example", pack.demoUrl, "button secondary", `Try ${pack.title} example${accessLabel}`));
    actions.append(link("View code ↗", pack.repoUrl, "repo-link", `${pack.title} repository${accessLabel}`));
    card.append(actions);
    if (!pack.demoUrl) {
      const note = element("p", "example-note");
      if (internal) {
        note.textContent = "Access-controlled showcase. Not a public customer deployment template.";
      } else {
        note.append(link("Try this example locally", pack.repoUrl, "", `Local setup instructions for ${pack.title}`), " with sample data using the Quick Start.");
      }
      card.append(note);
    }
    return card;
  }

  function comingCard() {
    const card = element("article", "pack-card coming-card");
    const icon = element("span", "coming-icon", "+");
    icon.setAttribute("aria-hidden", "true");
    card.append(icon, element("h3", "", "More to explore soon."), element("p", "", "Check back for more ideas across industries and business challenges."));
    return card;
  }

  function render() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const matches = packs.filter(pack => {
      const content = [pack.title, pack.summary, pack.industry, pack.function, ...pack.features, ...(pack.tags || [])].join(" ").toLocaleLowerCase();
      return terms.every(term => content.includes(term)) && Object.entries(selection).every(([key, value]) => !value || pack[key] === value);
    });
    grid.replaceChildren(...matches.map(packCard), comingCard());
    empty.hidden = matches.length !== 0;
    status.textContent = `${matches.length} ${matches.length === 1 ? "pack" : "packs"} shown · ${packs.length} in the collection`;
  }

  function reset() {
    search.value = "";
    Object.keys(selection).forEach(key => { selection[key] = ""; });
    updateChips();
    render();
    search.focus();
  }

  async function load() {
    error.hidden = true;
    empty.hidden = true;
    status.textContent = "Loading the collection…";
    search.disabled = true;
    document.querySelector("#reset-filters").disabled = true;
    document.querySelector("#retry-load").disabled = true;
    filters.replaceChildren();
    grid.replaceChildren();
    try {
      const response = await fetch("./packs.json", { credentials: "omit" });
      if (!response.ok) throw new Error(`Catalog request failed (${response.status}).`);
      packs = validateCatalog(await response.json());
      buildFilters();
      render();
      const latest = packs.map(pack => pack.updated).sort().at(-1);
      document.querySelector("#catalog-updated").textContent = latest ? `Latest pack review ${latest}` : "";
      search.disabled = false;
      document.querySelector("#reset-filters").disabled = false;
    } catch (failure) {
      error.hidden = false;
      status.textContent = "Collection unavailable.";
      console.error("Snow Packs:", failure.message);
    } finally {
      document.querySelector("#retry-load").disabled = false;
    }
  }

  search.addEventListener("input", render);
  document.querySelector("#reset-filters").addEventListener("click", reset);
  document.querySelector("#reset-empty").addEventListener("click", reset);
  document.querySelector("#retry-load").addEventListener("click", load);
  load();
})();
