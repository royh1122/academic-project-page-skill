# Maintaining the skill

Notes for people changing the skill itself. The agent using the skill never needs them, so they live outside `skills/academic-project-page/`.

- **Release:** bump the version in `skills/academic-project-page/SKILL.md`, `.claude-plugin/marketplace.json` and `skills/.codex-plugin/plugin.json` (CI fails when they differ), add a CHANGELOG entry, and rerun the core evals in `evals/evals.json` for any change in behaviour (topic evals only when their area changes; a no-skill baseline only for a new eval or rule).
- **Finding ids:** every audit message gets a stable id from the pattern table in `scripts/lib/findings.mjs` (the first match wins; unmatched messages fall back to their check's name). Give a new check's message a distinctive start and add its id there.
- **Planted flaws:** `python evals/check_fixtures.py` serves each fixture in `eval-kit/fixtures/` and checks that the audit reports every defect's `audit_id` (CI runs it). `--coverage` (no browser; CI runs it too) fails when an id in `findings.mjs` has no planted flaw and no entry in the script's `UNTESTED` list, so a new check ships with a fixture.
- **False positives:** before releasing a new check, run the full audit on clean built pages (the current and the previous template, and a hand-written page) and expect no new findings.
- **Size budget:** CI warns when the SKILL.md body passes 2,200 words, fails at 2,500 words, and fails on any SKILL.md line over 700 characters. Each rule has one home: content-truth and reporting rules in SKILL.md, layout and media in `references/layout-polish.md`, theme values in `references/style-fidelity.md`, icons in `references/icons.md`. A new rule replaces or merges an old one, or goes in a reference.
- **Icons:** the template's icons are inline SVG from Font Awesome Free 6.7.2 (CC BY 4.0) and Academicons (SIL OFL 1.1). `references/icons.md` holds the set, and `static/js/index.js` holds the four carousel icons.

## The typography check (`check_style.js`)

`scripts/check_style.js` compares computed styles with `references/theme-profile.json` and inspects the face Chromium actually rendered (`CSS.getPlatformFontsForNode`) for the title, authors, and body, because a declared family can silently fall back to Arial. `node scripts/audit.mjs <url>` runs it; it finds the profile next to the skill, or at `$THEME_PROFILE`, or takes a parsed profile as its second argument.

Profile format: `tolerances` (`px` for lengths and line heights, `weight` for font weights, `color` per RGB channel), then `rules`, each `{ "selector", "expect": { property: value }, "optional" }`. Numbers are pixels or weights; `#rrggbb` values are colours; `fontFamily` matches the first family in the computed list; anything else must match exactly. A single value can carry its own tolerance as `{ "value": 48, "tolerance": 1 }`. `renderedFonts` lists `{ selector, family }` pairs for the rendered-face check.

To change the theme deliberately, change the CSS, re-measure on a filled page, update the profile and this file together, and confirm the check still fails when the fonts are forced to Arial. For a one-off requested redesign, pass `--skip-style` and state the changed expectations.

Under `playwright-cli run-code --filename scripts/check_style.js`, set `THEME_PROFILE` to the profile's path. If fonts cannot load or the browser cannot report the rendered face, report the check as incomplete; a CSS family name is not proof.

## Defects fixed relative to APT (checked at APT commit `d38af1c`; values measured 2026-10-28)

| APT | This bundle |
| --- | --- |
| `<main>` never closed; two `id="results-carousel"`; `h4`/`h5` in the More Works menu before the `h1`; captions as `h2.subtitle` | `<main>` closed before the footer; class-based carousels; menu and captions use non-heading markup |
| Icon-only close button without a label; menu toggle without `aria-expanded`; iframe and PDF iframe without `title` | Labels on every icon-only control; `aria-expanded`/`aria-controls`; titled embeds |
| `--text-light #94a3b8`, `--text-secondary #64748b` on tints, green "Copied" `#10b981`, award `#ef4444` (alarm-red on pink) | AA colours above |
| Accent bar fixed at `left: 50%` under left-aligned headings | Bar follows the heading's alignment |
| Fixed More Works button and scroll-to-top button stacked over content at the bottom right on phones | Menu in the page flow; one optional contents pill that hides while reading down wherever it would cover the column |
| bulma-carousel autoplay every 5 s with no pause control; cloned slides exposed; carousel videos played regardless of motion preference | Rotation off by default, opt-in with a pause control; no clones, hidden slides inert; video play gated on visibility, current slide, and motion preference |
| Entrance animation and smooth scrolling for everyone | Only under `prefers-reduced-motion: no-preference` |
| "Cop" + CSS `::after` "ied!" with no announcement | Label set in JavaScript and announced in a live region |
| Videos without `playsinline`, poster, or dimensions | All three, plus a download fallback |
| jQuery, Adobe View SDK, bulma-slider, bulma-carousel, Font Awesome loaded twice (CSS without its webfonts, and JS) | Plain JavaScript; inline SVG icons (Font Awesome SVG JavaScript before v1.3.0); Bulma kept |
| JSON-LD declared CC BY 4.0 for the paper | No licence claimed; add the paper's own licence if it has one |
