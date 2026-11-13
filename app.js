"use strict";

(() => {
  const search = document.querySelector("#search");
  const filters = document.querySelector("#filters");
  const grid = document.querySelector("#pack-grid");
  const status = document.querySelector("#results-status");
  const error = document.querySelector("#load-error");
  const empty = document.querySelector("#empty-state");
  const outcomeTiles = document.querySelector("#outcome-tiles");
  const dialog = document.querySelector("#pack-dialog");
  const drawer = document.querySelector("#drawer-content");
  const copyStatus = document.querySelector("#copy-status");
  const selection = { industry: "", function: "", outcome: "" };
  let packs = [];
  let openPackId = "";

  const SVG_NS = "http://www.w3.org/2000/svg";

  // Business outcomes shown as tiles above the filters. Each pack's `outcome` must be one of these ids.
  const OUTCOMES = [
    { id: "catch-financial-crime", title: "Catch financial crime", blurb: "Spot suspicious activity faster and explain every alert.", icon: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM21 21l-5-5" },
    { id: "prove-compliance", title: "Prove compliance", blurb: "Answer regulators and govern sensitive data with confidence.", icon: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6zM9 12l2 2 4-4" },
    { id: "manage-risk", title: "Manage risk", blurb: "See exposures, reserves, and early warning signals sooner.", icon: "M4 17a8 8 0 0 1 16 0M12 17l4-5M3 21h18" },
    { id: "serve-clients", title: "Serve clients better", blurb: "Understand customers and help teams act on insight.", icon: "M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM2 20a6 6 0 0 1 12 0M16 11a3 3 0 1 0 0-6M16 14a6 6 0 0 1 6 6" },
  ];

  // Color and icon per industry, for card headers. Unknown industries fall back to the Snowflake blue hexagon.
  const INDUSTRIES = {
    "Banking": { color: "#2f6fde", icon: "M3 10h18M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18M12 3l9 5H3z" },
    "Insurance": { color: "#0f9488", icon: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6zM9 12l2 2 4-4" },
    "Capital Markets": { color: "#7c4ddb", icon: "M3 17l5-5 4 3 8-8M14 7h6v6" },
    "Wealth Management": { color: "#c27a12", icon: "M6 4h12l3 5-9 11L3 9zM3 9h18M9 4l3 5 3-5" },
    "Asset Management": { color: "#d0457f", icon: "M12 3v9h9M21 12a9 9 0 1 1-9-9" },
    "Payments": { color: "#0a8fb0", icon: "M3 6h18v12H3zM3 10h18M7 15h4" },
    "Financial Services": { color: "#11567f", icon: "M4 21V8l8-5 8 5v13M9 21v-6h6v6" },
  };
  const DEFAULT_INDUSTRY = { color: "#29b5e8", icon: "M12 2l8.7 5v10L12 22l-8.7-5V7z" };

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function link(text, url, className, accessibleLabel) {
    const node = element("a", className, text);
    node.href = url;
    // Every catalog link leaves the site, so it opens in a new tab and says so to screen readers.
    node.target = "_blank";
    node.rel = "noopener noreferrer";
    node.setAttribute("aria-label", `${accessibleLabel || text.replace(/[↗▶]/g, "").trim()} (opens in a new tab)`);
    return node;
  }

  function icon(path, className) {
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "1.8");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");
    if (className) svg.setAttribute("class", className);
    const shape = document.createElementNS(SVG_NS, "path");
    shape.setAttribute("d", path);
    svg.append(shape);
    return svg;
  }

  function industryStyle(industry) {
    return INDUSTRIES[industry] || DEFAULT_INDUSTRY;
  }

  // Decorative colored band with the industry's icon at the top of a card or the detail panel.
  function industryBand(pack, className = "card-visual") {
    const style = industryStyle(pack.industry);
    const band = element("div", className);
    band.setAttribute("aria-hidden", "true");
    band.style.setProperty("--ind", style.color);
    band.append(icon(style.icon, "band-icon"), icon(style.icon, "band-watermark"));
    return band;
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
    const outcomeIds = new Set(OUTCOMES.map(outcome => outcome.id));
    for (const pack of data) {
      if (!pack || requiredText.some(key => typeof pack[key] !== "string" || !pack[key].trim())) {
        throw new Error("Missing required pack metadata.");
      }
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(pack.id) || ids.has(pack.id)) throw new Error("Invalid or duplicate pack ID.");
      if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(pack.updated)) throw new Error("Invalid review month.");
      if (pack.workInProgress !== undefined && typeof pack.workInProgress !== "boolean") throw new Error("Invalid work-in-progress flag.");
      const placeholder = pack.workInProgress === true;
      if (!Array.isArray(pack.features) || (!placeholder && !pack.features.length) || pack.features.some(tag => typeof tag !== "string" || !tag.trim())) throw new Error("Invalid feature tags.");
      if (placeholder && (pack.features.length || [pack.pagesUrl, pack.repoUrl, pack.demoUrl].some(url => url !== ""))) throw new Error("Placeholders must not claim capabilities or link to unfinished resources.");
      if (pack.tags !== undefined && (!Array.isArray(pack.tags) || pack.tags.some(tag => typeof tag !== "string"))) throw new Error("Invalid search tags.");
      if (!safeUrl(pack.pagesUrl, placeholder) || !safeUrl(pack.repoUrl, placeholder) || !safeUrl(pack.demoUrl, true)) throw new Error("Pack links must be HTTPS.");
      if (pack.setup !== undefined && !(!placeholder && ["local", "snowflake"].includes(pack.setup))) throw new Error("Invalid setup mode.");
      if (pack.outcome !== undefined && !outcomeIds.has(pack.outcome)) throw new Error("Invalid outcome.");
      if (pack.images !== undefined && (placeholder || !Array.isArray(pack.images) || !pack.images.length || pack.images.length > 8 || pack.images.some(image => !image || typeof image.src !== "string" || !/^assets\/packs\/[a-z0-9-]+\.(jpg|png|webp)$/.test(image.src) || typeof image.alt !== "string" || !image.alt.trim()))) throw new Error("Invalid pack images.");
      if (pack.access !== undefined && !["public", "internal"].includes(pack.access)) throw new Error("Invalid access label.");
      ids.add(pack.id);
    }
    return data;
  }

  // ---------- Hero screenshot wall ----------

  // Set to false to show only the original hero art.
  const HERO_WALL = true;
  const WALL_FIRST_MS = 2500;  // card art on arrival
  const WALL_SHOW_MS = 14000;  // screenshot wall
  const WALL_ART_MS = 8000;    // card art between rounds

  function buildHeroWall() {
    const wall = document.querySelector("#hero-wall");
    // Deal one screenshot per pack in turn so neighbouring tiles come from different packs.
    const sources = packs.filter(pack => !pack.workInProgress && pack.images)
      .sort((a, b) => b.images.length - a.images.length);
    const shots = [];
    for (let i = 0; i < Math.max(0, ...sources.map(pack => pack.images.length)); i++) {
      for (const pack of sources) if (pack.images[i]) shots.push({ ...pack.images[i], title: pack.title });
    }
    // With reduced motion the card art stays put.
    if (shots.length < 4 || matchMedia("(prefers-reduced-motion: reduce)").matches) {
      wall.hidden = true;
      return;
    }
    const columns = [shots.filter((_, n) => n % 2 === 0), shots.filter((_, n) => n % 2 === 1)];
    wall.replaceChildren(...columns.map((column, n) => {
      const track = element("div", `wall-track wall-track-${n + 1}`);
      // Each column is listed twice so the scroll animation can loop seamlessly.
      for (const shot of [...column, ...column]) {
        const tile = element("figure", "wall-tile");
        const img = element("img");
        img.src = shot.src;
        img.alt = "";
        img.width = 960;
        img.height = 600;
        img.decoding = "async";
        tile.append(img, element("figcaption", "", shot.title));
        track.append(tile);
      }
      const column_ = element("div", "wall-column");
      column_.append(track);
      return column_;
    }));
    wall.hidden = false;
    const art = wall.parentElement;
    art.classList.add("has-wall");
    // Card art first, then the wall, alternating with a crossfade.
    const cycle = showWall => {
      art.classList.toggle("show-wall", showWall);
      setTimeout(() => cycle(!showWall), showWall ? WALL_SHOW_MS : WALL_ART_MS);
    };
    setTimeout(() => cycle(true), WALL_FIRST_MS);
  }

  // ---------- Outcome tiles and filters ----------

  function buildOutcomes() {
    outcomeTiles.replaceChildren(...OUTCOMES.map(outcome => {
      const tile = element("button", "outcome-tile");
      tile.type = "button";
      tile.dataset.outcome = outcome.id;
      tile.setAttribute("aria-pressed", String(selection.outcome === outcome.id));
      const text = element("span", "outcome-text");
      text.append(element("strong", "", outcome.title), element("span", "outcome-blurb", outcome.blurb));
      tile.append(icon(outcome.icon, "outcome-icon"), text);
      tile.addEventListener("click", () => {
        selection.outcome = selection.outcome === outcome.id ? "" : outcome.id;
        updateChips();
        render();
      });
      return tile;
    }));
  }

  function buildFilters() {
    filters.replaceChildren();
    for (const [key, label, all] of [["industry", "Industry", "All industries"], ["function", "Function", "All functions"]]) {
      const wrap = element("div", "filter-select");
      const select = element("select");
      select.id = `filter-${key}`;
      select.dataset.filter = key;
      const name = element("label", "sr-only", label);
      name.htmlFor = select.id;
      const choices = [...new Set(packs.map(pack => pack[key]))].sort();
      select.append(new Option(all, ""));
      for (const value of choices) {
        const count = packs.filter(pack => pack[key] === value).length;
        select.append(new Option(`${value} (${count})`, value));
      }
      select.value = selection[key];
      select.addEventListener("change", () => {
        selection[key] = select.value;
        updateChips();
        render();
      });
      wrap.append(name, select);
      filters.append(wrap);
    }
  }

  function updateChips() {
    filters.querySelectorAll("select").forEach(select => {
      select.value = selection[select.dataset.filter];
      select.classList.toggle("active", Boolean(select.value));
    });
    outcomeTiles.querySelectorAll("button").forEach(tile => {
      tile.setAttribute("aria-pressed", String(selection.outcome === tile.dataset.outcome));
    });
  }

  // ---------- Cards ----------

  function packCard(pack) {
    const internal = pack.access === "internal";
    const card = element("article", "pack-card");
    card.dataset.packId = pack.id;
    const headingId = `pack-${pack.id}`;
    card.setAttribute("aria-labelledby", headingId);
    const badges = element("div", "card-top");
    badges.append(element("span", "badge", pack.industry), element("span", "badge function-badge", pack.function));
    const heading = element("h3");
    heading.id = headingId;
    card.append(industryBand(pack), badges, heading, element("p", "pack-summary", pack.summary));
    if (pack.workInProgress) {
      heading.textContent = pack.title;
      card.classList.add("wip-card");
      card.insertBefore(element("p", "wip-label", "Work in progress"), card.firstChild.nextSibling);
      card.append(element("p", "wip-note", "Planned concept. Example and code are not yet available."));
      return card;
    }
    card.classList.add("available-card");
    const titleButton = element("button", "title-button", pack.title);
    titleButton.type = "button";
    titleButton.setAttribute("aria-haspopup", "dialog");
    titleButton.addEventListener("click", () => openDetails(pack.id, titleButton));
    heading.append(titleButton);
    const quick = element("span", "card-quick");
    // Hosted apps lead with Try it!; any card with screenshots also keeps its Preview.
    if (pack.demoUrl) quick.append(link("▶ Try it!", pack.demoUrl, "try-link", `Try ${pack.title}${internal ? "; employee sign-in required" : ""}`));
    if (pack.images) quick.append(previewToggle(pack, card));
    if (quick.childElementCount) badges.append(quick);
    if (internal) card.append(element("p", "access-note", "Internal · Snowflake employees only"));
    const features = element("ul", "feature-tags");
    features.setAttribute("aria-label", "Snowflake features and capabilities");
    pack.features.forEach(feature => features.append(element("li", "", feature)));
    card.append(features);
    const actions = element("div", "card-actions");
    const accessLabel = internal ? "; employee sign-in required" : "";
    actions.append(link("View pack ↗", pack.pagesUrl, "button primary", `View ${pack.title}${accessLabel}`));
    const details = element("button", "details-link", "Details");
    details.type = "button";
    details.setAttribute("aria-haspopup", "dialog");
    details.setAttribute("aria-label", `${pack.title} details`);
    details.addEventListener("click", () => openDetails(pack.id, details));
    actions.append(details, link("View code ↗", pack.repoUrl, "repo-link", `${pack.title} repository${accessLabel}`));
    card.append(actions);
    if (!pack.demoUrl) {
      const note = element("p", "example-note");
      if (internal) {
        note.textContent = "Access-controlled showcase. Not a public customer deployment template.";
      } else if (pack.setup === "snowflake") {
        note.append(link("Try this example in your Snowflake account", pack.repoUrl, "", `Setup instructions for ${pack.title}`), " with synthetic data using the guide's SQL script.");
      } else {
        note.append(link("Try this example locally", pack.repoUrl, "", `Local setup instructions for ${pack.title}`), " with sample data using the Quick Start.");
      }
      card.append(note);
    }
    return card;
  }

  // Hover, focus, or tap the toggle to show a screenshot carousel over the card.
  // Images are created on first open, so cards stay light until someone asks.
  function previewToggle(pack, card) {
    const panelId = `preview-${pack.id}`;
    const toggle = element("button", "preview-toggle");
    toggle.type = "button";
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", panelId);
    const play = element("span", "preview-icon", "▶");
    play.setAttribute("aria-hidden", "true");
    toggle.append(play, " Preview");
    toggle.setAttribute("aria-label", `Preview ${pack.title} screenshots`);

    const panel = element("div", "preview-panel");
    panel.id = panelId;
    panel.hidden = true;
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-label", `${pack.title} screenshots`);
    let slides = [];
    let dots = [];
    let caption;
    let index = 0;
    let timer;
    let closeTimer;
    let pinned = false;
    let suppressOpen = false;
    let openedBy = "";
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    function build() {
      const frame = link("", pack.pagesUrl, "preview-frame");
      frame.tabIndex = -1;
      frame.setAttribute("aria-hidden", "true");
      slides = pack.images.map((image, n) => {
        const img = element("img");
        img.src = image.src;
        img.alt = image.alt;
        img.width = 960;
        img.height = 600;
        img.decoding = "async";
        img.className = n === 0 ? "active" : "";
        frame.append(img);
        return img;
      });
      caption = element("p", "preview-caption");
      caption.setAttribute("aria-live", "polite");
      const nav = element("div", "preview-dots");
      dots = pack.images.map((image, n) => {
        const dot = element("button", "preview-dot");
        dot.type = "button";
        dot.setAttribute("aria-label", `Screenshot ${n + 1} of ${pack.images.length}: ${image.alt}`);
        dot.addEventListener("click", () => { stopCycle(); show(n); });
        nav.append(dot);
        return dot;
      });
      panel.append(frame, caption, nav);
    }

    function show(n) {
      index = (n + slides.length) % slides.length;
      slides.forEach((img, i) => img.classList.toggle("active", i === index));
      dots.forEach((dot, i) => dot.setAttribute("aria-current", String(i === index)));
      caption.textContent = `${index + 1}/${slides.length} · ${pack.images[index].alt}`;
    }

    function stopCycle() {
      clearInterval(timer);
      timer = undefined;
    }

    function open(source) {
      clearTimeout(closeTimer);
      if (suppressOpen || !panel.hidden) return;
      openedBy = source;
      if (!slides.length) build();
      document.querySelectorAll(".preview-toggle[aria-expanded='true']").forEach(other => {
        if (other !== toggle) other.dispatchEvent(new CustomEvent("preview-close"));
      });
      panel.style.top = `${toggle.offsetTop + toggle.offsetHeight + 10}px`;
      panel.hidden = false;
      toggle.setAttribute("aria-expanded", "true");
      show(0);
      if (!reduceMotion.matches && slides.length > 1) timer = setInterval(() => show(index + 1), 2200);
    }

    function close() {
      stopCycle();
      pinned = false;
      panel.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    }

    function closeSoon() {
      if (pinned) return;
      clearTimeout(closeTimer);
      closeTimer = setTimeout(() => {
        const hovered = panel.matches(":hover") || toggle.matches(":hover");
        const focused = card.contains(document.activeElement);
        if (!hovered && (openedBy === "pointer" || !focused)) close();
      }, 150);
    }

    toggle.addEventListener("mouseenter", () => open("pointer"));
    toggle.addEventListener("focus", () => open("keyboard"));
    toggle.addEventListener("click", () => {
      if (panel.hidden) { open("pointer"); pinned = true; }
      else if (pinned) close();
      else pinned = true;
    });
    toggle.addEventListener("mouseleave", closeSoon);
    toggle.addEventListener("preview-close", close);
    panel.addEventListener("mouseenter", () => clearTimeout(closeTimer));
    panel.addEventListener("mouseleave", closeSoon);
    card.addEventListener("focusout", event => {
      if (!card.contains(event.relatedTarget)) { pinned = false; closeSoon(); }
    });
    card.addEventListener("keydown", event => {
      if (event.key === "Escape" && !panel.hidden) {
        close();
        suppressOpen = true;
        toggle.focus({ preventScroll: true });
        suppressOpen = false;
      }
    });
    card.append(panel);
    return toggle;
  }

  // ---------- Detail panel ----------

  function cocoPrompt(pack) {
    const where = pack.setup === "snowflake"
      ? "in my Snowflake account using a least-privilege role and its synthetic data"
      : "on its synthetic sample data without connecting to my Snowflake account";
    return `Clone ${pack.repoUrl} and follow its README to run the ${pack.title} example ${where}. Then explain the data model and propose how to map it to my own development tables. Show me the plan before creating or changing anything.`;
  }

  function copyButton(label, getText, className = "button secondary") {
    const button = element("button", className, label);
    button.type = "button";
    button.addEventListener("click", async () => {
      const ok = await copyText(getText());
      button.textContent = ok ? "Copied" : "Copy failed";
      copyStatus.textContent = ok ? `${label}: copied to clipboard.` : "Copy failed. Select the text and copy it manually.";
      setTimeout(() => { button.textContent = label; }, 1800);
    });
    return button;
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const area = element("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.append(area);
      area.select();
      let ok = false;
      try { ok = document.execCommand("copy"); } catch { ok = false; }
      area.remove();
      return ok;
    }
  }

  function gallery(pack) {
    const box = element("div", "drawer-gallery");
    const main = element("img", "drawer-shot");
    main.width = 960;
    main.height = 600;
    const caption = element("p", "drawer-caption");
    const thumbs = element("div", "drawer-thumbs");
    const select = n => {
      main.src = pack.images[n].src;
      main.alt = pack.images[n].alt;
      caption.textContent = pack.images[n].alt;
      thumbs.querySelectorAll("button").forEach((thumb, i) => thumb.setAttribute("aria-current", String(i === n)));
    };
    pack.images.forEach((image, n) => {
      const thumb = element("button", "drawer-thumb");
      thumb.type = "button";
      thumb.setAttribute("aria-label", `Show screenshot ${n + 1}: ${image.alt}`);
      const img = element("img");
      img.src = image.src;
      img.alt = "";
      img.width = 160;
      img.height = 100;
      thumb.append(img);
      thumb.addEventListener("click", () => select(n));
      thumbs.append(thumb);
    });
    box.append(main, caption);
    if (pack.images.length > 1) box.append(thumbs);
    select(0);
    return box;
  }

  function section(title, ...content) {
    const block = element("section", "drawer-section");
    block.append(element("h3", "", title), ...content);
    return block;
  }

  function renderDetails(pack) {
    const outcome = OUTCOMES.find(item => item.id === pack.outcome);
    const badges = element("div", "card-top");
    badges.append(element("span", "badge", pack.industry), element("span", "badge function-badge", pack.function));
    const title = element("h2", "drawer-title", pack.title);
    title.id = "drawer-title";
    const parts = [industryBand(pack, "drawer-visual"), badges, title, element("p", "drawer-summary", pack.summary)];
    if (outcome) {
      const chip = element("p", "drawer-outcome");
      chip.append(icon(outcome.icon, "outcome-icon"), outcome.title);
      parts.push(chip);
    }
    if (pack.images) parts.push(gallery(pack));
    const features = element("ul", "feature-tags");
    pack.features.forEach(feature => features.append(element("li", "", feature)));
    parts.push(section("Snowflake capabilities", features));
    const runs = pack.demoUrl
      ? "Opens in your browser on synthetic data, with no account or install. To run it in your own Snowflake account, follow the repository's deploy steps."
      : pack.setup === "snowflake"
      ? "Runs in your own Snowflake account on synthetic data, using the guide's SQL script. Review permissions and costs first."
      : "Runs on bundled sample data without a Snowflake account. Follow the Quick Start in the repository.";
    parts.push(section("Try it", element("p", "", runs)));
    const prompt = element("pre", "coco-prompt");
    prompt.textContent = cocoPrompt(pack);
    parts.push(section("Make it yours with Cortex Code", element("p", "", "Open Cortex Code and paste this prompt to get started:"), prompt, copyButton("Copy prompt", () => cocoPrompt(pack))));
    const actions = element("div", "drawer-actions");
    if (pack.demoUrl) actions.append(link("▶ Try it!", pack.demoUrl, "button primary", `Try ${pack.title}`));
    actions.append(
      link("View pack ↗", pack.pagesUrl, pack.demoUrl ? "button secondary" : "button primary", `View ${pack.title}`),
      link("View code ↗", pack.repoUrl, "button secondary", `${pack.title} repository`),
      copyButton("Copy link", () => shareUrl({ pack: pack.id }), "button secondary"),
    );
    parts.push(actions, element("p", "drawer-note", "An illustrative starting point on synthetic data, not a production-ready solution."));
    drawer.replaceChildren(...parts);
  }

  let lastTrigger = null;

  function openDetails(id, trigger) {
    const pack = packs.find(item => item.id === id && !item.workInProgress);
    if (!pack) return;
    lastTrigger = trigger || null;
    openPackId = id;
    renderDetails(pack);
    if (!dialog.open) dialog.showModal();
    dialog.scrollTop = 0;
    document.querySelector("#drawer-close").focus();
    syncUrl();
  }

  dialog.addEventListener("close", () => {
    const closedId = openPackId;
    openPackId = "";
    syncUrl();
    // Return focus to whatever opened the panel, or to the pack's title when it was opened from a shared link.
    const fallback = grid.querySelector(`[data-pack-id="${CSS.escape(closedId)}"] .title-button`);
    const target = lastTrigger && document.contains(lastTrigger) ? lastTrigger : fallback;
    if (target) target.focus({ preventScroll: true });
  });
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
  document.querySelector("#drawer-close").addEventListener("click", () => dialog.close());

  // ---------- Shareable URLs ----------

  function viewState() {
    return { q: search.value.trim(), industry: selection.industry, function: selection.function, outcome: selection.outcome, pack: openPackId };
  }

  function shareUrl(overrides = {}) {
    const state = { ...viewState(), ...overrides };
    const params = new URLSearchParams();
    for (const key of ["q", "outcome", "industry", "function", "pack"]) {
      if (state[key]) params.set(key, state[key]);
    }
    const query = params.toString();
    return `${location.origin}${location.pathname}${query ? `?${query}` : ""}`;
  }

  function syncUrl() {
    const url = shareUrl();
    if (url !== location.href.split("#")[0]) history.replaceState(null, "", url + location.hash);
  }

  // Apply ?q=&outcome=&industry=&function=&pack= from the address bar, ignoring unknown values.
  function applyUrl() {
    const params = new URLSearchParams(location.search);
    const known = key => new Set(packs.map(pack => pack[key]));
    const q = (params.get("q") || "").slice(0, 100);
    if (q) search.value = q;
    if (known("industry").has(params.get("industry"))) selection.industry = params.get("industry");
    if (known("function").has(params.get("function"))) selection.function = params.get("function");
    if (OUTCOMES.some(outcome => outcome.id === params.get("outcome"))) selection.outcome = params.get("outcome");
    const pack = params.get("pack");
    const shared = Boolean(q || selection.industry || selection.function || selection.outcome || pack);
    return { pack, shared };
  }

  // ---------- Render ----------

  function render() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const matches = packs.filter(pack => {
      const outcome = OUTCOMES.find(item => item.id === pack.outcome);
      const content = [pack.title, pack.summary, pack.industry, pack.function, outcome?.title || "", ...pack.features, ...(pack.tags || [])].join(" ").toLocaleLowerCase();
      return terms.every(term => content.includes(term)) && Object.entries(selection).every(([key, value]) => !value || pack[key] === value);
    });
    matches.sort((first, second) => Number(Boolean(first.workInProgress)) - Number(Boolean(second.workInProgress)));
    grid.replaceChildren(...matches.map(packCard));
    empty.hidden = matches.length !== 0;
    const planned = matches.filter(pack => pack.workInProgress).length;
    status.textContent = `${matches.length} ${matches.length === 1 ? "pack" : "packs"} shown · ${packs.length} in the collection · ${planned} work in progress`;
    syncUrl();
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
    document.querySelector("#copy-view").disabled = true;
    document.querySelector("#retry-load").disabled = true;
    filters.replaceChildren();
    outcomeTiles.replaceChildren();
    grid.replaceChildren();
    try {
      const response = await fetch("./packs.json", { credentials: "omit", cache: "no-cache" });
      if (!response.ok) throw new Error(`Catalog request failed (${response.status}).`);
      packs = validateCatalog(await response.json());
      const { pack, shared } = applyUrl();
      if (HERO_WALL) buildHeroWall();
      buildOutcomes();
      buildFilters();
      render();
      search.disabled = false;
      document.querySelector("#reset-filters").disabled = false;
      document.querySelector("#copy-view").disabled = false;
      if (shared) document.querySelector("#catalog").scrollIntoView();
      if (pack) openDetails(pack);
    } catch (failure) {
      error.hidden = false;
      status.textContent = "Collection unavailable.";
      console.error("Snow Packs:", failure.message);
    } finally {
      document.querySelector("#retry-load").disabled = false;
    }
  }

  const copyView = document.querySelector("#copy-view");
  copyView.addEventListener("click", async () => {
    const label = "Copy link to this view";
    const ok = await copyText(shareUrl({ pack: "" }));
    copyView.textContent = ok ? "Link copied" : "Copy failed";
    copyStatus.textContent = ok ? "Link to this view copied to clipboard." : "Copy failed.";
    setTimeout(() => { copyView.textContent = label; }, 1800);
  });
  search.addEventListener("input", render);
  document.querySelector("#reset-filters").addEventListener("click", reset);
  document.querySelector("#reset-empty").addEventListener("click", reset);
  document.querySelector("#retry-load").addEventListener("click", load);
  load();
})();
