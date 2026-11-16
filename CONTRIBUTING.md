# Contribute a Snow Pack

Use this guide while you build, so your repository is ready to list in [Snow Packs](https://sfc-gh-ooral.github.io/snow-packs/) without rework. The catalog is customer-facing: readers are business and technical people at customers and prospects.

A pack has three parts: a **GitHub Pages guide** (its landing page), an **app** customers can click through, and a **public repository** with the code. Snow Packs links to the guide and the repository and shows a screenshot of the app on its card.

**Every new pack ships an app.** Many business leaders never log in to Snowflake or don't have permission to run code, so the app must also work in a **no-account mode** on synthetic data. They should be able to click around and see what's possible in minutes. Script- or worksheet-only packs are no longer accepted as new listings; existing ones are being upgraded with front ends.

**Must** items are required before listing. **Should** items are strongly recommended; call out any you skip in your pull request.

## 1. Pick the use case

- **Must:** Start from a business problem a specific industry recognizes (e.g., "reproduce a regulatory report as filed"), not from a feature ("a Time Travel demo").
- **Must:** Choose one primary **industry** and one **business function**. Reuse existing catalog labels where possible: Banking, Insurance, Payments, Capital Markets, Wealth Management, Asset Management, Financial Services · Finance, Operations, Risk, Compliance, Claims, Underwriting, Advisory, Investments. New labels automatically become filter chips.
- **Should:** Check the catalog first. If your idea matches a **Work in progress** concept, say so in your pull request; your pack replaces that placeholder.

## 2. Repository setup

- **Must:** A public repository under your GitHub account, named `sfguide-<short-topic>` in lowercase with hyphens.
- **Must:** A `LICENSE` file. Use **Apache 2.0** to match the catalog. Without a license, nobody can legally reuse or adapt the code.
- **Must:** GitHub Pages enabled (**Settings > Pages > Deploy from a branch**, `main`, `/ (root)` or `/docs`). Add `.nojekyll` if you use folders starting with `_`.
- **Should:** Turn on **Settings > Template repository** so readers get a **Use this template** button. A documented fork/clone path is acceptable.
- **Should:** Add a short repository description and topics (e.g., `snowflake`, `financial-services`, `compliance`).

Suggested layout:

```text
README.md                 Setup, prerequisites, customization, owner, review date
LICENSE                   Apache 2.0
index.html  (+ css/js)    The GitHub Pages guide
app/                      The app (local web app or Streamlit), with a mock-data mode
sql/<topic>.sql           Snowflake setup: objects, synthetic data, and cleanup
data/                     Synthetic data or captured sample results
docs/images/              App screenshots for the guide and the catalog card
```

## 3. The landing page

Write for a customer seeing it for the first time. The landing page is your pitch: make it as polished and visual as possible, so readers can picture exactly what they could have.

- **Must:** Lead with the business problem and outcome on the first screen, in plain language: a one-line headline and a one-paragraph scenario.
- **Must:** Show the finished end product with **screenshots of the running app** (see [Capture screenshots with CoCo](#capture-screenshots-with-coco)). Readers should understand the result without running anything.
- **Must:** Give every screenshot a caption that says what the reader is looking at and which Snowflake capability produced it, plus alt text.
- **Should:** Tell the story with several screenshots (overview first, then key drill-downs), or a short captioned video or GIF of the main workflow.
- **Must:** Name the Snowflake capability behind each step or component (e.g., "MATCH_RECOGNIZE finds the spoofing sequence"). Only claim capabilities you used and tested.
- **Must:** Show a visible disclaimer: synthetic data, illustrative logic, not production or regulatory/compliance advice.
- **Must:** Link to the repository and relevant Snowflake documentation.
- **Should:** Show prerequisites, time to complete, and expected cost near the top.
- **Should:** Work on a phone-width screen and in dark mode.
- **Should:** Avoid trackers and analytics. Bundle small libraries (e.g., a syntax highlighter) in the repository instead of loading them from a CDN.
- **Must not:** Use official Snowflake logo files or trademarked imagery. A generic icon or text wordmark is fine.
- **Must not:** Describe internal sales motions ("SEs use this to…", "customers ask us…"). Keep it about the reader's business.

### Capture screenshots with CoCo

Capture screenshots with a **script**, not by hand. A headless browser at a fixed window size produces large, sharp, identical images on any laptop. You don't need to maximize a window or plug in a monitor, and you can rerun the script whenever the UI changes. Because it starts a fresh browser with no sign-in, account details can't end up in a shot.

- **Should:** Add `scripts/capture-screenshots.mjs` and an `npm run capture` command. Copy the [Wealth Advisor Assistant script](https://github.com/sfc-gh-ooral/sfguide-wealth-advisor-assistant/blob/main/scripts/capture-screenshots.mjs) as a starting point. It:
  - serves your no-account example (e.g., `docs/try/`) locally, with no dev server or Snowflake account;
  - opens each screen in headless Chromium (Playwright) at a **1600×1000** viewport, the catalog's 16:10 shape, with a fixed locale and time zone;
  - clicks through the steps you list (open a drill-down, ask the agent, switch personas);
  - writes landing-page images to `docs/images/` at 1.25× (2000×1250 PNG) and catalog cards at 0.6× (960×600 JPG), ready for section 11.
- **Should not:** Attach the script to your everyday, signed-in browser (e.g., Chrome over a remote-debugging port). That session can show account URLs, user names, and internal tabs. Use it only for an app that cannot run without signing in, and review every frame.

To set it up, ask CoCo: "Copy the capture script from the Wealth Advisor Assistant pack, adapt the `SHOTS` list to my app's main workflow, run it, and show me every image." Then:

1. Review every image: synthetic data only, no account URLs, user names, tokens, or internal tabs.
2. Ask CoCo to add the images to the landing page with captions and alt text, then check the page at desktop and phone width.

Keep images in the repository (e.g., `docs/images/`), ideally under 500 KB each. The built-in CoCo browser still works if you can't run a script: maximize its window first so shots aren't squeezed into a narrow panel.

**Optional video.** A 15–30 second captioned clip or GIF of the main workflow helps a lot on the landing page. Record it the same way: Playwright's video recording, or frames from a headless run, encoded locally with a tool such as ffmpeg. Every number on screen must come from the pack's synthetic data. Don't add claims, stock footage, or mock UI.

## 4. The app

The app is what customers remember. Build an experience for the people who would use it day to day, such as an investigator inbox, a portfolio dashboard, or a chat with an agent, not a tour of SQL.

- **Must:** An end-user app with a real workflow: navigation, drill-downs, and the key decision or action. Any of these work:
  - A **local web app** (e.g., React or another framework) that also connects to Snowflake.
  - **Streamlit in Snowflake**, or an app on **Snowpark Container Services**.
  - A **Cortex Agent** or **Cortex Analyst** chat experience inside an app.
- **Must:** A **no-account mode**: the app runs on bundled synthetic data with **no Snowflake account, credentials, or installs beyond the README's quick start**. Set `setup` to `local` in the catalog entry. A hosted static version on GitHub Pages is even better; put its URL in `demoUrl` so the card shows **Try it!**. A working example replaces the card's screenshot **Preview**; the screenshots still appear in the pack's details and in the site's header.
- **Must:** In no-account mode, clearly label anything simulated, such as "Sample AI response" for mocked Cortex output versus live inference.
- **Must:** A **live mode** that runs the same app against Snowflake on synthetic data, so readers can see the real capabilities and adapt it to their own data.
- **Should:** A **Sample / Live switch** in the app header that always shows which mode is on. Default to Live when a Snowflake connection is configured, and let readers stay in Sample mode even when one is. If there's no connection and the reader picks Live, show the setup steps (for example, the `.env.local` lines and the restart command) or a link to the README. Never collect Snowflake credentials in the browser. The hosted GitHub Pages example is always Sample mode, so its switch should point to the repository's live-mode guide. Don't fall back silently: if a live call fails, show the error rather than sample data.
- **Should:** Make simulated AI calls feel like real ones. In Sample mode, wait a few seconds before showing a scripted answer (for example, 4 to 8 seconds, with a little jitter) and show staged progress steps that name what the live path really does, such as "Applying row access policy", "Generating SQL with Cortex Analyst", and "Checking the response with Cortex Guard". Keep the scripted answer labeled as a sample. In Live mode, show the same steps while the real call runs, with no added delay, and report the measured latency. Keep the steps truthful: only list work the live path performs.
- **Should:** Make the Snowflake capability visible in the UI, e.g., a small "Powered by Cortex Agents" or "Row access policy applied" badge on the component that uses it.
- **Should:** Polish matters: consistent styling, realistic synthetic names and numbers, no empty states or error screens in the main flow.

### Add a front end with CoCo

Already have a working SQL script or notebook? Ask CoCo to build the app on top of it. For example:

- "Build a Streamlit app on top of the views in `sql/<topic>.sql`: an alert queue sorted by severity, with a drill-down that shows each case's timeline. Add a mock-data mode that reads `data/sample_results.json` so it runs without a Snowflake connection."
- "Turn this guide into a local React app with a sidebar, a KPI dashboard, and a detail page. Use the captured results as mock data, and label every mocked AI response."
- "Add a 'View as' role switcher that shows how the same data looks to each persona, using the row access and masking policies in the script."
- "Add a Sample / Live switch to the header. When there's no Snowflake connection, show the setup steps instead of switching. In Sample mode, make each AI button wait a few seconds and show staged reasoning steps that match what the live call does."

Then ask CoCo to run the app, click through the workflow, and capture the screenshots for the landing page and catalog card with a capture script (see [Capture screenshots with CoCo](#capture-screenshots-with-coco)).

## 5. Snowflake setup and sample data

- **Must:** Run entirely on **synthetic data** generated by or shipped with the repository. Deterministic generation (same numbers every run) is ideal, so screenshots match what readers get.
- **Must:** Keep Snowflake setup self-contained: create a dedicated database and warehouse (XSMALL, short auto-suspend) and change nothing that already exists.
- **Must:** Include a cleanup step that removes everything the setup created: databases, warehouses, roles, tasks, apps, and dynamic tables.
- **Should:** Run setup top to bottom in one worksheet or notebook, with no find-and-replace.

## 6. Security and least privilege

- **Must:** Keep credentials, tokens, keys, account identifiers, secret-bearing URLs, and internal hostnames out of code, screenshots, sample output, and **commit history**. If something leaks, revoke it immediately, then rewrite history. Report it through the hosting platform's private security process; never repeat it in an issue.
- **Must:** Redact user names in captured output (e.g., `<YOUR_USER>`).
- **Should:** Offer a **least-privilege path**, not only `USE ROLE ACCOUNTADMIN`: a short block that creates a demo role with only the grants the example needs. Regulated customers will ask.
- **Should:** Note edition requirements (e.g., Enterprise for masking, Access History, or Time Travel beyond one day) and a Standard Edition fallback where possible.

## 7. Customer data and confidentiality

- **Must not:** Include customer names, logos, data, identifiers, account details, or identifiable business logic, even renamed. Start from synthetic data, not scrubbed customer records.
- **Must not:** Reference deals, internal programs, internal-only projects, or non-public roadmap features.
- **Must:** Use generally available features or clearly labeled preview features.

## 8. The README: deploy and adapt

- **Must:** Prerequisites: edition, role, features, tested versions, and regions if relevant.
- **Must:** Step-by-step run instructions and a list of what gets created; a table of objects works well.
- **Must:** Expected compute cost and time.
- **Must:** Known limitations, stated honestly (e.g., "Dynamic Tables don't support MATCH_RECOGNIZE, so spoofing runs on demand").
- **Must:** A **Customize with Cortex Code** section with two or three prompts tailored to your pack, such as:
  - "Explain this pack's data model and map it to my schema without changing any objects."
  - "Replace the synthetic data with my development tables. Propose least-privilege access and a validation plan first."
  - "Adjust the alert thresholds for my volumes and explain the trade-offs."
- **Must:** An **owner** and **last-reviewed date**, e.g., `Owner: Jane Doe · Last reviewed: November 2026`.
- **Must:** The license and an as-is disclaimer: an illustrative example, not an official Snowflake product, and not supported by Snowflake Support.

## 9. Claims and wording

- **Must:** Describe outcomes as possibilities ("helps analysts spot…"), not guarantees. Avoid unmeasured numbers such as "cuts review time 80%".
- **Must:** Qualify results from planted or synthetic cases, e.g., "12 alerts and no false positives **on this synthetic data set**".
- **Should:** Use "example", "guide", or "showcase" rather than "demo" on customer-facing pages.
- **Should:** Write short, plain sentences, and define industry acronyms once.

## 10. Before you submit

- [ ] Opened the Pages URL and repository in a signed-out browser window; both load correctly.
- [ ] Ran the example end to end in a clean account or role, then ran cleanup.
- [ ] Page output matches what the example produces today.
- [ ] Searched files and history for secrets and real names (e.g., `git log -p | grep -iE "password|token|secret|account"`).
- [ ] `LICENSE`, owner, and review date are present.
- [ ] The **Customize with Cortex Code** section is present.
- [ ] The app runs in no-account mode from a fresh clone using only the README quick start.
- [ ] Landing page shows captioned screenshots of the running app.
- [ ] Reviewed every screenshot for real data, account URLs, user names, and secrets.
- [ ] Checked the page at phone width.

## 11. Add your pack to the catalog

1. Fork this repository and create a branch.
2. Add one object to [`packs.json`](packs.json) using the schema below.
3. Add **2 to 8 card preview screenshots** of your app's key screens (main dashboard first), saved as `assets/packs/<id>-1.jpg`, `<id>-2.jpg`, and so on: 16:10, 960×600, ideally under 100 KB each. A capture script can write these for you. Readers see them in a carousel when they hover or tap **Preview** on your card (cards with a `demoUrl` show **Try it!** instead) and in the pack's details. They live in this repository, not yours, so the catalog never loads outside images.
4. Add one matching row to the **Catalog** table in [`README.md`](README.md).
5. Serve this site locally with `python3 -m http.server 8000 --bind 127.0.0.1`. Check search, filters, empty results, keyboard navigation, narrow layout, and both color schemes.
6. Open a pull request, complete the checklist, and note any skipped **Should** items or limitations.

**One JSON entry updates the whole website:** cards, filters, counts, and search. The README table is a separate human-readable mirror because GitHub Markdown cannot render `packs.json`. No site code changes or build step are needed.

Not ready to build yet? Use [the proposal form](https://github.com/sfc-gh-ooral/snow-packs/issues/new?template=pack-proposal.md).

### Catalog schema

```json
{
  "id": "contact-driver-analytics",
  "title": "Contact Driver Analytics",
  "summary": "Find opportunities to reduce repeat contacts and escalations by connecting call drivers, sentiment trends, and transcript insights in one view.",
  "industry": "Financial Services",
  "function": "Operations",
  "outcome": "serve-clients",
  "features": ["Cortex AI", "Sentiment Analysis", "Text Classification"],
  "tags": ["contact center", "calls", "customer experience"],
  "setup": "local",
  "images": [
    { "src": "assets/packs/contact-driver-analytics-1.jpg", "alt": "Dashboard: call volume, sentiment, and escalation KPIs with a weekly trend" },
    { "src": "assets/packs/contact-driver-analytics-2.jpg", "alt": "AI insights: executive summary, key findings, and recommendations from Cortex" }
  ],
  "pagesUrl": "https://YOUR-OWNER.github.io/YOUR-PACK/",
  "demoUrl": "",
  "repoUrl": "https://github.com/YOUR-OWNER/YOUR-PACK",
  "author": "Your name",
  "updated": "2026-11"
}
```

- `id`: unique, kebab-case.
- `summary`: one sentence, business outcome first, without unmeasured promises.
- `features`: a nonempty list of capabilities you verified.
- `pagesUrl`, `repoUrl`: verified, permanent HTTPS URLs. Never use authentication nonces or expiring signed URLs.
- `demoUrl`: a hosted, no-install example if one exists; otherwise an empty string, and the card points readers to the repository. Don't put local-server addresses or setup instructions here.
- `author`, `updated`: the owner and `YYYY-MM` of the latest review, matching the README. Published cards show the owner as **By Your Name**, and every owner appears in the **Built by** strip under the catalog.

Optional fields:

- `authorUrl`: optional link for your name on the card, e.g. `https://www.linkedin.com/in/your-handle`. Only LinkedIn profile URLs are accepted. Add only your own profile. Not allowed on work-in-progress entries.
- `outcome`: the business outcome tile the pack appears under: `catch-financial-crime`, `prove-compliance`, `manage-risk`, or `serve-clients`. Required for new packs. Ask the maintainers if none fits; new outcomes are added in `app.js`.
- `images`: 2–8 preview screenshots, each `{ "src": "assets/packs/<id>-<n>.jpg", "alt": "…" }` (`.jpg`, `.png`, or `.webp`). The `alt` text doubles as the carousel caption, so describe what the screen shows and which capability powers it. Required for new packs; at least 1 is enforced. Not allowed on work-in-progress entries.
- `setup`: `local` (default) when the app runs in no-account mode; `snowflake` only for older listings that run solely in the reader's account. See section 4. Not allowed on work-in-progress entries.
- `tags`: extra plain-text search terms. Feature tags are already searchable.
- `workInProgress`: boolean, default `false`. Use `true` only for an approved placeholder concept: set `features` to `[]` and all three URLs to empty strings, and describe the use case as planned, without implementation claims or release dates. The card shows **Work in progress** with no links or capability tags. Remove the flag and add verified capabilities and links when the pack is published.
- `access`: `public` (default) or `internal`. Internal listings need maintainer approval and public-safe descriptions only. This is a label, **not an access control**: all JSON is public, so the destination must enforce authentication.

## Keep it current

- Re-run the app and setup when Snowflake features or syntax change, refresh screenshots and the card previews if the UI changed, then update the review date in the README and catalog.
- Fix broken links quickly, and tell the maintainers if you move or archive the repository.
- Update validation notes when evidence is no longer current.
- If you step away, hand ownership to someone else or ask for the pack to be delisted.

Maintainers review additions against this guide. Listing is not an endorsement, certification, production approval, or Snowflake Support commitment, and metadata review is not end-to-end deployment validation.

## Disclaimer

Snow Packs are illustrative examples provided as-is, not official Snowflake products, and are not supported by Snowflake Support. They contain no customer data. Review and test before any production use.
