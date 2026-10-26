# Snow Packs

**Industry use cases built in the field. Ready to run in yours.**

Snow Packs is a catalog of industry-specific Snowflake use cases built by field Solution Engineers. Each pack aims to connect a business vision to a synthetic-data demo and reusable deployment code. Browse for inspiration, explore an example, and adapt it to your own environment with Cortex Code.

**[Browse the catalog](https://sfc-gh-ooral.github.io/snow-packs/) · [Contribute a pack](CONTRIBUTING.md) · [Propose an idea](https://github.com/sfc-gh-ooral/snow-packs/issues/new?template=pack-proposal.md)**

## See. Try. Deploy.

| See | Try | Deploy |
| --- | --- | --- |
| Understand the business problem and see the end product. | Explore synthetic data without a data connection; learn the capability behind each component. | Use the repo as a template, connect your data, and adapt with Cortex Code. |

## Catalog

| Pack | Industry | Function | Maturity | Links |
| --- | --- | --- | --- | --- |
| **Loss Triangle Suite** — Make reserve reviews more consistent with loss development analysis, segment comparisons, and AI-assisted actuarial Q&A. | Insurance | Finance | Demo | [View pack](https://sfc-gh-ooral.github.io/sfguide-loss-triangle-analysis/) · [Local demo setup](https://github.com/sfc-gh-ooral/sfguide-loss-triangle-analysis#quick-start-mock-data) · [Repo](https://github.com/sfc-gh-ooral/sfguide-loss-triangle-analysis) |
| **Contact Driver Analytics** — Find opportunities to reduce repeat contacts and escalations with call-driver, sentiment, and transcript insights. | Financial Services | Operations | Demo | [View pack](https://sfc-gh-ooral.github.io/sfguide-contact-driver-analytics/) · [Local demo setup](https://github.com/sfc-gh-ooral/sfguide-contact-driver-analytics#quick-start-mock-data) · [Repo](https://github.com/sfc-gh-ooral/sfguide-contact-driver-analytics) |
| **Snow Owl (internal)** — Prepare for more informed discovery conversations with sourced research and reusable account context. | Cross-industry | Sales | Demo | [View pack — employee access](https://effective-adventure-kmekk65.pages.github.io/) · [Internal repo](https://github.com/snowflake-corp/snow-owl) |

**More packs coming.** [Propose the next one](https://github.com/sfc-gh-ooral/snow-packs/issues/new?template=pack-proposal.md).

The two public packs provide local synthetic-data quick starts, not hosted demos, and currently support fork/clone rather than GitHub's **Use this template** button. Snow Owl is a clearly labeled, access-controlled internal reference: it is not a public customer deployment template, and its private content is not mirrored here. A sign-in redirect or an unauthenticated 404 for its repository is expected.

### What maturity means

- **Demo:** illustrative experience; synthetic or mock data. Initial entries use this conservative label; their deployment paths have not been independently certified by this catalog.
- **PoC-ready:** the owner has verified documented setup and data mapping in a clean account and recorded limitations and costs.
- **Pilot-ready:** additionally reviewed for scoped pilot operation, access controls, monitoring, and support ownership. Not a production guarantee.

## How to use a pack

1. **Browse** by industry, function, or business outcome.
2. **Try the demo.** Follow the local Quick Start when a hosted demo is not available. Mock AI responses are illustrative, not live inference.
3. **Fork the repo**, or select **Use this template** if the pack offers it.
4. **Deploy using its README** into your own Snowflake account. Review prerequisites, permissions, regional feature availability, and compute costs first.
5. **Adapt with Cortex Code.** Start in an isolated development environment and review generated changes before executing them.

Example customization prompts:

> Explain this pack's data model and map it to my sample schema without changing any objects.

> Replace the synthetic data with my development tables. Propose the least-privilege access and validation plan before making changes.

> Add a business-specific KPI and explain its calculation, tests, and limitations.

Never put customer data, secrets, or identifying business logic into a public issue, PR, or demo. Validate AI-generated output and involve the relevant business owner before relying on it.

## How to contribute

Read the [pack standard](CONTRIBUTING.md), then open a PR adding **one entry to `packs.json` and one row to the README catalog**. The site, cards, filters, counts, and feature search update from JSON alone; the README row is the separate human-readable mirror. No HTML or JavaScript edits are needed to add a pack.

Every new public pack needs a landing page, a no-connection synthetic-data demo, capability callouts, deploy/customization instructions, a named owner, and a last-reviewed date. Existing entries are an initial inventory, not a certification that every standard is already met.

## Run this catalog locally

From the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Opening `index.html` directly with `file://` does not support loading the JSON catalog reliably.

The published site is four static files: `index.html`, `styles.css`, `app.js`, and `packs.json`. There is no build step, framework, npm dependency, analytics, remote font, or third-party script. Search stays in the browser; the only catalog data request is same-origin `packs.json`.

### Checks

```bash
python3 -m json.tool packs.json
node --check app.js
# Optional browser regression tests (Python Playwright + Chromium required):
python3 -m unittest discover -s tests -v
```

The optional tests start their own localhost server and cover filters, search, links in rendered cards, error recovery, input safety, mobile overflow, color schemes, and basic keyboard access. They are not required to serve or deploy the site.

### GitHub Pages

In **Settings > Pages**, choose **Deploy from a branch**, branch **main**, folder **/ (root)**. `.nojekyll` is included. The [live catalog](https://sfc-gh-ooral.github.io/snow-packs/) updates after GitHub finishes publishing a push to `main`.

## License and disclaimer

The hub is licensed under [Apache 2.0](LICENSE). Linked packs retain their own licenses and access restrictions.

Snow Packs are field-built examples provided as-is, not official Snowflake products, and are not supported by Snowflake Support. They contain no customer data. Review and test before any production use.

Site and initial catalog metadata reviewed: **October 26, 2026**. Deployment readiness is a separate review.
