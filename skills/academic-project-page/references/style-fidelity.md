# Theme baseline

The bundled template uses one theme: the modern look of the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template) (APT), which was itself adapted from [Nerfies](https://github.com/nerfies/nerfies.github.io). Both are CC BY-SA 4.0; the footer credits both. This bundle keeps APT's typography, palette, cards, and accents, and fixes APT's accessibility and motion defects. Values below were measured in Chrome at 1440 × 1000 on the filled template.

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
| Award `.publication-awards` | 16 px | 600 | `#7c4a03` on `#fef3c7`, 1 px `#f3d98b` border, 12 px radius (the venue pill's shape); optional `fa-trophy` or `fa-award` icon in the text colour |
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
| `--award-color` / `--award-background` / `--award-border` | `#7c4a03` / `#fef3c7` / `#f3d98b` | award pill, 6.6:1 (APT's red `#ef4444` on pink: 3.4:1, and it read as an alert); the border is decoration. A re-themed page overrides the three tokens, keeping text 4.5:1 on its fill |
| `--accent-color`, `--gradient-accent` | `#0ea5e9`, `#f093fb → #f5576c` | decoration only, never text |
| `--background-secondary` / `--background-accent` / `--border-color` | `#f8fafc` / `#f1f5f9` / `#e2e8f0` | tinted bands, pills and code, hairlines |

Every text colour meets WCAG AA (4.5:1) on every background it is used on. Check any new colour against `#f1f5f9`, the darkest light background.

Further tokens, all on `:root` in `index.css` (and read by `figure-viewer.css`, which falls back to the default if one is missing):

| Token | Default | Use |
| --- | --- | --- |
| `--on-primary` | `#ffffff` | text on a `--primary-color` / `--primary-hover` fill: copy button, button and contents-pill hover |
| `--button-background` | `var(--text-primary)` | resource buttons, skip link, contents-pill toggle |
| `--on-button` | `var(--background-primary)` | their label colour; follows the two tokens above, so it flips by itself in a dark theme |
| `--on-success` | `#ffffff` | text on the `--success-color` fill |
| `--link-color` / `--link-hover` | `#3273dc` / `var(--text-strong)` | links in running text (transcript, poster); Bulma's blue |
| `--text-strong` | `#363636` | bold text, row headers, content headings, viewer controls; set it equal to `--text-primary` |
| `--shadow-sm` to `--shadow-xl`, `--border-radius*`, `--font-*` | | not colours of the palette, but overridable the same way |

Fixed on purpose: the video embed's `#0f172a` placeholder (it must be dark in any theme) and the figure viewer's neutral black shadows.

## Re-theming

A requested theme (dark, a lab colour) is one `:root` block placed after the defaults, with no component selectors. Override:

1. **Surfaces and text:** `--background-primary`, `--background-secondary`, `--background-accent`, `--border-color`, `--text-primary`, `--text-strong`, `--text-secondary`, `--text-light`. Add `color-scheme: dark` for a dark theme.
2. **Accent:** `--primary-color`, `--primary-hover`, `--accent-color`, `--gradient-accent`, and `--on-primary`, the text on accent fills. White is not right for every accent: orange `#f26b1d` takes dark text (`#0f172a`, 5.9:1), where white is 3.0:1. `--button-background` and `--on-button` need no override unless the buttons should be the accent.
3. **Links:** `--link-color` and `--link-hover`.
4. **State and award:** `--success-color` with `--on-success`; `--award-color`, `--award-background`, `--award-border`.
5. **Shadows,** darker on a dark page.

Every text/background pair must still pass 4.5:1, and focus rings and the dot and border strokes 3:1 against their surface (`--text-light` is also used for the carousel dots). A light-on-dark accent may need a lighter shade for text and links than for fills: a blue that is fine as a button fill fails as text on navy, so give `--link-color` and `--primary-color` (used for links, focus rings, and the author links) the lighter shade and pick `--on-primary` for it. Run `node scripts/audit.mjs <url> --skip-style` (the typography profile expects the default colours); the audit's contrast check covers the rest, then look at the screenshots for the buttons, tables, BibTeX block, carousel controls, captions, award pill, and contents pill.

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
- **Floating controls.** The More Works menu sits in the page flow above the title. The optional contents pill (`.page-nav`: a Contents button and back to top, bottom right) is the only fixed element. It stays hidden until the header is scrolled past, is icon-only on phones, and wherever it would overlap the text column steps aside while the reader scrolls down (it returns on any scroll up, at the end of the page, and while in use), so it never sits over text being read. The menu lists the page's `h2` headings, marks the current one with `aria-current="location"`, closes with Esc (focus returns to the button), and uses only palette tokens (`--text-primary`, `--background-primary`, `--border-color`, `--primary-*`, `--button-background`, `--on-button`, `--on-primary`), so a re-themed page recolours it. Delete the block on short pages.
- **Motion.** Entrance fade, smooth scrolling, hover lifts, and carousel slide transitions apply only under `prefers-reduced-motion: no-preference`.
- **Focus.** 3 px `--primary-color` (`#2563eb`) ring with 2 px offset on `:focus-visible` for links, buttons, and focusable regions.
- **Copy button.** The label changes in JavaScript ("Copied" / "Copy failed") and a visually hidden `role="status"` region announces the result.

## Typography check

`audit.mjs` compares the rendered page with these values (`references/theme-profile.json`) and checks the font face the browser actually drew, since a declared family can silently fall back to Arial. For a requested redesign, pass `--skip-style` and state the changed expectations. If the browser cannot report the rendered face, report the typography check as not run.
