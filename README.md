# Snow Packs

**Ideas for your industry. A head start for your business.**

Snow Packs is a catalog of industry-specific Snowflake showcases and starting points. Published examples connect business challenges to sample-data experiences and reusable code. Work-in-progress entries preview planned financial-services concepts; they do not yet include examples or code. Browse for inspiration, explore an example, and adapt it to your own environment with Cortex Code.

**[Browse the catalog](https://sfc-gh-ooral.github.io/snow-packs/) · [Contribute a pack](CONTRIBUTING.md) · [Propose an idea](https://github.com/sfc-gh-ooral/snow-packs/issues/new?template=pack-proposal.md)**

## See. Try. Deploy.

| See | Try | Deploy |
| --- | --- | --- |
| Understand the business problem and see the end product. | Explore synthetic data without a data connection; learn the capability behind each component. | Use the repo as a template, connect your data, and adapt with Cortex Code. |

## Catalog

| Pack | Industry | Function | Links |
| --- | --- | --- | --- |
| **Loss Triangle Suite** — Make reserve reviews more consistent with loss development analysis, segment comparisons, and AI-assisted actuarial Q&A. | Insurance | Finance | [View pack](https://sfc-gh-ooral.github.io/sfguide-loss-triangle-analysis/) · [Local example setup](https://github.com/sfc-gh-ooral/sfguide-loss-triangle-analysis#quick-start-mock-data) · [Repo](https://github.com/sfc-gh-ooral/sfguide-loss-triangle-analysis) |
| **Contact Driver Analytics** — Find opportunities to reduce repeat contacts and escalations with call-driver, sentiment, and transcript insights. | Financial Services | Operations | [View pack](https://sfc-gh-ooral.github.io/sfguide-contact-driver-analytics/) · [Local example setup](https://github.com/sfc-gh-ooral/sfguide-contact-driver-analytics#quick-start-mock-data) · [Repo](https://github.com/sfc-gh-ooral/sfguide-contact-driver-analytics) |
| **Credit Risk Monitor** — Borrower trends, concentrations, and early warning signals. | Banking | Risk | Work in progress |
| **Liquidity & Cash Flow** — Cash positions, funding needs, and liquidity scenarios. | Banking | Finance | Work in progress |
| **AML Investigation Workbench** — Transaction patterns and case evidence for investigator-led reviews. | Banking | Compliance | Work in progress |
| **KYC & Onboarding Insights** — Documentation gaps, onboarding bottlenecks, and review queues. | Banking | Compliance | Work in progress |
| **Payment Fraud Insights** — Suspicious payment patterns and investigation outcomes. | Payments | Risk | Work in progress |
| **Claims Triage Insights** — Claim complexity and handling delays for adjuster-led prioritization. | Insurance | Claims | Work in progress |
| **Underwriting Submission Review** — Submission completeness, risk context, and portfolio fit. | Insurance | Underwriting | Work in progress |
| **Trade Surveillance Workbench** — Order and execution patterns in market context. | Capital Markets | Compliance | Work in progress |
| **Client Portfolio Review** — Holdings, concentration, and allocation drift for advisor conversations. | Wealth Management | Advisory | Work in progress |
| **Investment Research Workbench** — Company filings, research notes, and supporting evidence. | Asset Management | Investments | Work in progress |

**12 packs: 2 published examples and 10 work-in-progress concepts.** [Propose the next one](https://github.com/sfc-gh-ooral/snow-packs/issues/new?template=pack-proposal.md).

The two public packs provide local synthetic-data quick starts, not hosted examples, and currently support fork/clone rather than GitHub's **Use this template** button. The ten placeholders describe intended use cases only, without implementation claims or release dates.

Packs are showcases and starting points, not production certifications. Review each pack's setup requirements, validation evidence, costs, and limitations before adapting it.

## How to use a pack

1. **Browse** by industry, function, or business outcome.
2. **Try the example.** Follow the local Quick Start when a hosted example is not available. Mock AI responses are illustrative, not live inference.
3. **Fork the repo**, or select **Use this template** if the pack offers it.
4. **Deploy using its README** into your own Snowflake account. Review prerequisites, permissions, regional feature availability, and compute costs first.
5. **Adapt with Cortex Code.** Start in an isolated development environment and review generated changes before executing them.

Example customization prompts:

> Explain this pack's data model and map it to my sample schema without changing any objects.

> Replace the synthetic data with my development tables. Propose the least-privilege access and validation plan before making changes.

> Add a business-specific KPI and explain its calculation, tests, and limitations.

Never put customer data, secrets, or identifying business logic into a public issue, PR, or example. Validate AI-generated output and involve the relevant business owner before relying on it.

## How to contribute

Read the [pack standard](CONTRIBUTING.md), then open a PR adding **one entry to `packs.json` and one row to the README catalog**. The site, cards, filters, counts, and feature search update from JSON alone; the README row is the separate human-readable mirror. No HTML or JavaScript edits are needed to add a pack.

Before publishing an example, each pack needs a landing page, a no-connection synthetic-data example, capability callouts, deploy/customization instructions, a named owner, and a last-reviewed date. Existing entries are an initial inventory, not a certification that every standard is already met.

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

Snow Packs are illustrative examples provided as-is, not official Snowflake products, and are not supported by Snowflake Support. They contain no customer data. Review and test before any production use.

Site and initial catalog metadata reviewed: **October 26, 2026**. Deployment readiness is a separate review.
