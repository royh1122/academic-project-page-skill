# Theme baseline

The bundled template uses one theme: the modern look of the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template) (APT, checked at commit `d38af1c`), which was itself adapted from [Nerfies](https://github.com/nerfies/nerfies.github.io). Both are CC BY-SA 4.0; the footer credits both. This bundle keeps APT's typography, palette, cards, and accents, and fixes APT's accessibility and motion defects (listed at the end). Values below were measured in Chrome at 1440 × 1000 on the template filled with sample content, on 2026-10-28. `references/theme-profile.json` holds the same values for the automated check.

## Typography

One family, Inter, requested from Google Fonts css2 at the five weights the CSS uses: `family=Inter:wght@400;500;600;700;800`. A 400-only request renders synthesized bold for every heading.

| Element | Size / line height | Weight | Colour |
| --- | --- | --- | --- |
| Body | 16 / 25.6 px (1.6) | 400 | `#1e293b` |
| Title `.publication-title` (`h1.title.is-1`) | 48 / 52.8 px (1.1); 40 px at ≤768 px, 32 px at ≤480 px | 800 | `#1e293b` |
| Authors `.publication-authors` | 20 / 32 px; 17 px at ≤768 px | 500 | `#1e293b` |
| Author links | as authors | 600 | `#2563eb` (5.2:1), gradient underline on hover/focus |
| Affiliations `.publication-affiliations` | 20 / 32 px; 17 px at ≤768 px | 400 | `#475569` |
| Equal-contribution note `.eql-cntrb` | 14 px, italic; its `sup` stays ≥12 px | 400 | `#5b6576` |
| Venue / status `.publication-venue` | 16 px | 600 | `#475569` on `#f1f5f9` pill |
| Award `.publication-awards` | 16 px | 700 | `#b91c1c` on `#fef2f2`, 4 px left border |
| Resource buttons `.publication-links .button` | 16 px | 600 | white on `#1e293b`; hover `#2563eb`; 12 px radius |
| Section heading `h2.title.is-3` | 32 / 36 px | 700 | `#1e293b`; 60 × 3 px gradient accent bar 16 px below |
| Sub-heading `h3.title.is-4` | 24 px | 600 | `#1e293b` |
| Abstract `.content.has-text-justified` | 17.6 / 31.68 px (1.1rem / 1.8); 16 px at ≤768 px | 400 | `#475569` |
| Teaser caption `.teaser-caption` | 18 / 28.8 px, centered | 400 | `#475569` |
| Figure and table captions | 15 px, upright, left-aligned (carousel captions centered) | 400 | `#475569`; label in `<strong>` |
| BibTeX `pre` | 14.4 px, `SF Mono, Monaco, Cascadia Code, Consolas, Roboto Mono, monospace` | 400 | `#1e293b` on `#f1f5f9` |
| Footer | 16 px / 1.7 | 400 | `#475569`; links `#2563eb`, underlined |

## Palette (CSS custom properties in `static/css/index.css`)

| Token | Value | Use and contrast |
| --- | --- | --- |
| `--primary-color` | `#2563eb` | links, copy button, focus ring; 5.2:1 on white, 4.7:1 on `#f1f5f9` |
| `--primary-hover` | `#1d4ed8` | hover |
| `--text-primary` | `#1e293b` | body, headings, dark buttons |
| `--text-secondary` | `#475569` | abstract, captions, affiliations, footer; 6.9:1 on `#f1f5f9` (APT `#64748b`: 4.3:1) |
| `--text-light` | `#5b6576` | notes, venues in the More Works list; 5.4:1 on `#f1f5f9` (APT `#94a3b8`: 2.6:1) |
| `--success-color` | `#047857` | "Copied" state, white text 5.5:1 (APT `#10b981`: 2.5:1) |
| `--award-color` / `--award-background` | `#b91c1c` / `#fef2f2` | award pill, 5.9:1 (APT `#ef4444`: 3.4:1) |
| `--accent-color`, `--gradient-accent` | `#0ea5e9`, `#f093fb → #f5576c` | decoration only, never text |
| `--background-secondary` / `--background-accent` / `--border-color` | `#f8fafc` / `#f1f5f9` / `#e2e8f0` | tinted bands, pills and code, hairlines |

Every text colour meets WCAG AA (4.5:1) on every background it is used on. Check any new colour against `#f1f5f9`, the darkest light background.

## Spacing and layout

| Element | Value |
| --- | --- |
| Main container `.container.is-max-desktop` | max 960 px; every section uses it, so all content shares one column |
| Sections `section.section` | 64 px top and bottom, 24 px sides; 48 / 16 px at ≤768 px |
| Tinted band `.section.is-light` | `#f8fafc` with `#e2e8f0` hairlines; alternate with plain sections |
| Title block `.publication-header .hero-body` | 48 px top, 32 px bottom |
| Teaser `.teaser .hero-body` | 16 px top, 48 px bottom |
| Section heading | 32 px below (including the accent bar) |
| Footer | `#f8fafc`, 48 px top and bottom, hairline above |
| Radii | 12 px for media, buttons, pills, code; 16 px for carousel cards and the More Works panel |
| Shadows | `--shadow-lg` on the teaser, `--shadow-xl` on the video embed; cards use a border, not a shadow |

## Component rules

- **Headings.** Centered (with a centered accent bar) only inside the centered reading column (`.columns.is-centered.has-text-centered > .column.is-four-fifths`: Abstract, Video). Everywhere else headings are left-aligned and the bar sits under the first letter. The bar is a block `::after`, so it follows the heading's alignment rather than a fixed `left: 50%`.
- **Heading order.** One `h1` (the title), then `h2` per section, `h3` inside sections. Menus, captions, and slide labels are not headings.
- **Media.** One corner treatment (12 px) for all content media. Videos: `playsinline`, `poster`, `width`/`height`, a download link as fallback; loops `autoplay muted loop` only when short and silent, with `reduced-motion.js`. YouTube: `youtube-nocookie.com`, `loading="lazy"`, a `title`, dark placeholder background.
- **Carousels.** `static/js/index.js`, no library. One slide at a time; off-screen slides are `inert` and `aria-hidden`; previous/next/dot buttons are labelled; no rotation unless `data-autoplay` is set, in which case a pause/play button appears and rotation stops on hover and focus and never starts under reduced motion. Muted carousel videos play only while their slide is current and on screen. Without JavaScript, slides stack.
- **Poster.** `<object type="application/pdf" title>` with a link inside; a download button below; below 769 px the embed is hidden and only the link remains.
- **Tables.** `.table-figure` pattern: caption above, natural width, scrolling keyboard-focusable container, `is-numeric` right alignment.
- **Floating controls.** None on phones. The More Works menu sits in the page flow above the title; the back-to-top button appears only at ≥1280 px, where it sits in the gutter beside the 960 px column.
- **Motion.** Entrance fade, smooth scrolling, hover lifts, and carousel slide transitions apply only under `prefers-reduced-motion: no-preference`.
- **Focus.** 3 px `#2563eb` ring with 2 px offset on `:focus-visible` for links, buttons, and focusable regions.
- **Copy button.** The label changes in JavaScript ("Copied" / "Copy failed") and a visually hidden `role="status"` region announces the result.

## Automated check

`scripts/check_style.js` compares computed styles with `references/theme-profile.json` and inspects the face Chromium actually rendered (`CSS.getPlatformFontsForNode`) for the title, authors, and body, because a declared family can silently fall back to Arial. `node scripts/audit.mjs <url>` runs it; it finds the profile next to the skill, or at `$THEME_PROFILE`, or takes a parsed profile as its second argument.

Profile format: `tolerances` (`px` for lengths and line heights, `weight` for font weights, `color` per RGB channel), then `rules`, each `{ "selector", "expect": { property: value }, "optional" }`. Numbers are pixels or weights; `#rrggbb` values are colours; `fontFamily` matches the first family in the computed list; anything else must match exactly. A single value can carry its own tolerance as `{ "value": 48, "tolerance": 1 }`. `renderedFonts` lists `{ selector, family }` pairs for the rendered-face check.

To change the theme deliberately, change the CSS, re-measure on a filled page, update the profile and this file together, and confirm the check still fails when the fonts are forced to Arial. For a one-off requested redesign, pass `--skip-style` and state the changed expectations.

Under `playwright-cli run-code --filename scripts/check_style.js`, set `THEME_PROFILE` to the profile's path. If fonts cannot load or the browser cannot report the rendered face, report the check as incomplete; a CSS family name is not proof.

## Defects fixed relative to APT

| APT | This bundle |
| --- | --- |
| `<main>` never closed; two `id="results-carousel"`; `h4`/`h5` in the More Works menu before the `h1`; captions as `h2.subtitle` | `<main>` closed before the footer; class-based carousels; menu and captions use non-heading markup |
| Icon-only close button without a label; menu toggle without `aria-expanded`; iframe and PDF iframe without `title` | Labels on every icon-only control; `aria-expanded`/`aria-controls`; titled embeds |
| `--text-light #94a3b8`, `--text-secondary #64748b` on tints, green "Copied" `#10b981`, award `#ef4444` | AA colours above |
| Accent bar fixed at `left: 50%` under left-aligned headings | Bar follows the heading's alignment |
| Fixed More Works button and scroll-to-top button stacked over content at the bottom right on phones | Menu in the page flow; back-to-top only in the desktop gutter |
| bulma-carousel autoplay every 5 s with no pause control; cloned slides exposed; carousel videos played regardless of motion preference | Rotation off by default, opt-in with a pause control; no clones, hidden slides inert; video play gated on visibility, current slide, and motion preference |
| Entrance animation and smooth scrolling for everyone | Only under `prefers-reduced-motion: no-preference` |
| "Cop" + CSS `::after` "ied!" with no announcement | Label set in JavaScript and announced in a live region |
| Videos without `playsinline`, poster, or dimensions | All three, plus a download fallback |
| jQuery, Adobe View SDK, bulma-slider, bulma-carousel, Font Awesome loaded twice (CSS without its webfonts, and JS) | Plain JavaScript; Font Awesome SVG JavaScript only; Bulma kept |
| JSON-LD declared CC BY 4.0 for the paper | No licence claimed; add the paper's own licence if it has one |
