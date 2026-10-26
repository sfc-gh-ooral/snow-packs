# Contribute a Snow Pack

A pack starts with a business outcome, not a feature tour. Make it easy for someone else to understand, try, and adapt your work.

## The pack standard

Every new public pack must include:

1. **A GitHub Pages landing page** explaining the business problem and solution vision, with screenshots or a video of the end product. Use synthetic examples and accessible image descriptions or video captions.
2. **A synthetic-data demo mode** that needs no Snowflake connection, credentials, or access to customer data. A local demo is fine; document its prerequisites and commands. Clearly distinguish mocked AI responses from live inference.
3. **In-app capability callouts** naming the Snowflake capability behind each component. Describe what is simulated versus executed; do not claim deployment modes or features that have not been verified.
4. **A deployment README** with prerequisites, tested versions, account/region requirements, setup and teardown steps, data contracts, expected compute costs, and known limitations. Include a **Customize with Cortex Code** section with example prompts.
5. **A clean public artifact:** no customer names, logos, data, identifiers, or identifiable business logic. No credentials, private keys, tokens, internal reports, or secrets in files, screenshots, URLs, or commit history. Use synthetic data from the start, not renamed customer records. Do not use official Snowflake logo files or trademarked imagery in this catalog.
6. **A named owner and a last-reviewed date** in the pack README. Set `author` and `updated` in the catalog to match the latest metadata review; record deployment validation separately.

Prefer enabling GitHub's **Template repository** option when appropriate so users can select **Use this template**. A fork/clone path is acceptable when clearly documented. Confirm an appropriate license and the as-is disclaimer.

## Add a pack

1. Fork this hub and create a branch for your contribution.
2. Verify your pack against the standard and test its links while signed out.
3. Add one object to the array in [`packs.json`](packs.json), using the schema below. Reuse industry/function labels where possible; new labels automatically become filter chips.
4. Add one row to the **Catalog** table in [`README.md`](README.md), with matching title, industry, function, maturity, and links.
5. Serve this hub locally using `python3 -m http.server 8000 --bind 127.0.0.1`. Check search, all filter groups, empty results, keyboard navigation, narrow layout, and both system color schemes.
6. Open a pull request and complete the pack-standard checklist. Include your review date and any exceptions or limitations.

**One JSON entry updates the whole website.** The README table is maintained separately because GitHub Markdown cannot dynamically render `packs.json`. No site code edits or build commands are required for a new pack.

## Catalog schema

```json
{
  "id": "inventory-planning",
  "title": "Inventory Planning",
  "summary": "Reduce stockout risk by identifying products that need replenishment attention.",
  "industry": "Retail",
  "function": "Operations",
  "features": ["Snowflake SQL"],
  "maturity": "Demo",
  "pagesUrl": "https://YOUR-OWNER.github.io/YOUR-PACK/",
  "demoUrl": "",
  "repoUrl": "https://github.com/YOUR-OWNER/YOUR-PACK",
  "author": "Your name",
  "updated": "2026-10"
}
```

Replace example URLs with verified, permanent HTTPS URLs. Never submit authentication nonces or expiring signed URLs. `id` must be unique and kebab-case; `updated` is `YYYY-MM`; `features` is a nonempty array of verified capabilities. `summary` is one sentence, business outcome first, without unmeasured promises. `demoUrl` must be an empty string if there is no hosted demo; the card omits **Try demo** and points readers to the repo. Do not put local-server addresses or deployment instructions in `demoUrl`.

Optional fields:

- `access`: `public` (default) or `internal`. Internal listings require maintainer approval and public-safe descriptions only. This flag is a label, **not an access control**: all JSON is public. The destination must enforce authentication.
- `tags`: additional plain-text search terms. Feature tags are already searchable without this field.

Snow Owl is an explicitly approved internal reference. It is not evidence that a customer can access or deploy it; its Pages and repository links remain access-controlled. Internal reference exceptions must be disclosed in the README and review, not silently treated as compliant public packs.

## Choose maturity honestly

| Label | Required evidence |
| --- | --- |
| Demo | An illustrative synthetic-data experience; clearly identify simulated features and local versus hosted execution. |
| PoC-ready | Documented deployment and data mapping tested in a clean account, with test date, prerequisites, costs, and limitations. |
| Pilot-ready | PoC evidence plus scoped security review, least-privilege access, monitoring, rollback/teardown, and a named pilot support owner. |

No label means production-approved, supported by Snowflake Support, or suitable for regulated decisions without review. Initial catalog entries are conservatively labeled Demo; catalog metadata review is not end-to-end deployment validation.

## Customize with Cortex Code: example prompts

Include prompts adapted to your pack, such as:

> Explain the application's data contracts. Propose a mapping from my development schema and identify missing fields; do not change anything yet.

> Add a new KPI with an explicit business definition and focused tests. Keep the no-connection demo functional.

> Review deployment permissions and propose a least-privilege setup, cost controls, and teardown plan before executing changes.

## Review and maintenance

Maintain the synthetic demo when APIs change. Retest links, update the last-reviewed date after review, and document breaking changes. Downgrade maturity when evidence is no longer current. Report exposed credentials through the hosting platform's private security process and revoke them immediately; never repeat them in an issue.

Use [the proposal form](https://github.com/sfc-gh-ooral/snow-packs/issues/new?template=pack-proposal.md) for ideas that are not ready for catalog inclusion. Additions are reviewed by maintainers; submitting a PR does not imply endorsement or certification.

## Disclaimer

Snow Packs are field-built examples provided as-is, not official Snowflake products, and are not supported by Snowflake Support. They contain no customer data. Review and test before any production use.
