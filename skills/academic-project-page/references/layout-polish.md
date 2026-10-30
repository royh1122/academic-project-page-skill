# Layout and polish contract

Read this before arranging media. Part 1 applies to any academic project page, whatever its theme, so it also guides a Polish of an existing page. Part 2 covers the bundled template's components. These rules keep a page consistent; they do not prescribe a layout. Which sections exist, their order, and how media are grouped follow the project's material. `node scripts/audit.mjs <url>` checks the mechanical parts and saves screenshots; the rest needs your eyes on those screenshots.

## Part 1: Core rules

### Alignment

- Each section uses one column: a centered reading column or the full content width. Within a section, every heading, paragraph, figure, table, and disclosure starts at that column's left edge. Side-by-side columns each start at their own edge. A block indented under a full-width grid is a defect.
- List markers and the indented text of list items are normal typography, not a second left edge; keep lists as lists.
- Center headings only in centered-column sections; left-align them in full-width sections. Use the same choice for every section of the same type.
- Cap long paragraphs in full-width sections at a reading measure (about 768 px) without centering them.

### Teaser

- One medium: full content width at its natural aspect ratio.
- Two or more media side by side: give each one `width: 100%; height: auto`, and set grid columns proportional to each medium's width ÷ height so they share one height at every width:

  ```css
  /* Columns = each medium's width/height ratio, e.g. a 4:3 image beside a 16:9 video: 1.333 and 1.778.
     minmax(0, ...) lets columns shrink below the media's natural width, so the proportions hold. */
  .teaser-grid { display: grid; grid-template-columns: minmax(0, 1.333fr) minmax(0, 1.778fr); gap: 1.5rem; align-items: start; }
  @media (max-width: 600px) { .teaser-grid { grid-template-columns: 1fr; } }
  ```

- Never combine a fixed `height` with `object-fit: contain` for teaser media: it letterboxes and misaligns the visible edges.
- One caption per medium, or one caption for the group, not both. Do not refer to media by position ("left", "right"): they stack on phones.
- Open with a teaser whenever the project has any visual. The teaser shows the project's main finding or outcome: whichever visual a visitor would most want to see first, in whatever form the project has it (a result image or plot, a demo or result clip, a qualitative example, a before/after, a screenshot of the working system). Prefer the visual that is legible at 375 px and needs the least explanation. Use the overview or method diagram only when the method itself is the contribution or no outcome visual exists or reads at that size; then the method section refers to it instead of repeating it.
- Prefer a teaser whose key content is legible in the 375 px screenshot. A dense multi-panel figure is the last choice for the teaser; if it is used, make it zoomable, and never drop the teaser only because the best visual is dense.

### Figures

- If the project has a method, pipeline, or architecture figure, show it inline with its explanation (or as the teaser). Disclosures and carousels hold secondary material only.
- Crop large empty margins from every figure before placing it (padding from plotting or diagram tools makes the content read small), then update its `width` and `height`.
- Each image appears once on the page. If the teaser shows a figure, later sections show different material. Duplicate files with different names count as the same image.
- Grids of figures: give every cell the same box (`height` with `object-fit: contain` is fine inside a grid cell) and crop source whitespace so figures have similar visual weight.
- Corners: one treatment for comparable media in content sections. Do not mix rounded and square.
- Figures that readers need to inspect closely (dense diagrams, screenshots, plots, comparison grids) get `data-zoom` and the bundled figure viewer. Do not write a custom lightbox.
- Captions state only what the data shows: check a reused caption's claims (trends, "best", "grows with") against the tables before keeping them.
- Captions describe the figure, not its position on the page ("the plot below", "Figure 3 in the paper") and not panels the page does not show.

### Video

- Short silent loops (results, comparisons): `autoplay muted loop playsinline`, with `static/js/reduced-motion.js`, which pauses them for visitors who prefer reduced motion.
- Videos with speech or an audio track, or longer than about 30 s: `controls playsinline preload="none"`, a poster, a captions track (`<track kind="captions">`), and a transcript link. Never autoplay them.
- Every local video: explicit `width`/`height`, a poster unless it autoplays, and a fallback download link. Embedded YouTube or Vimeo videos: the privacy-enhanced domain where one exists, `loading="lazy"`, and a `title`.
- Convert GIFs and re-encode large recordings to H.264 MP4 with square pixels and even dimensions; a non-square sample aspect ratio makes the browser display a different shape than the file's pixel size, which breaks equal-height layouts:

  ```bash
  ffmpeg -i input.gif -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw*sar/2)*2:trunc(ih/2)*2,setsar=1" -an output.mp4
  ```

- Choose local poster frames deliberately: extract candidates, look at them, and pick a representative frame with no typos, black frames, or mid-transition blur.

### Motion

- Nothing moves by itself for visitors who prefer reduced motion: no autoplaying video, no rotating carousel, no entrance animation, no smooth scrolling. The audit reloads the page with reduced motion emulated and fails on anything still moving.
- Rotation of any kind needs a visible pause control and stops on hover and focus.

### Text

- Load every weight the CSS uses. A family loaded at 400 only renders synthesized bold for titles and headings; the audit warns on it.
- `text-wrap: balance` for the title, author and affiliation lines, and headings; `text-wrap: pretty` for paragraphs and captions only (on list items it causes early breaks).
- Tables: caption above, natural width, a keyboard-focusable scrolling container on narrow screens; cells do not wrap, the container scrolls. Right-align numeric columns and left-align text columns. Do not stretch narrow tables to full width.
- In the title only, keep hyphenated terms (such as Non-Autoregressive) from breaking at the hyphen. In body text a break at a hyphen is normal.
- In the header (status, venue, award lines), keep year ranges and short labels together, for example "2025–2026" inside `<span class="nowrap">`.
- An in-page navigation, if any, has one link per section with labels matching the section headings. The template's contents menu builds itself from the `h2` headings, so it matches by construction; a hand-written nav must be checked.

### Header

- **Venue, status, awards, author links:** only what SKILL.md's Build step 2 verifies. Without a verified venue, the user's own status wording (Preprint, Research in preparation) may take the venue line. Mention a finalist or nomination only in the user's words if they ask.
- **Resource buttons:** one per verified resource. Private repositories and unreleased data get no button.
- **Button and link wording:** say what it does or where it goes ("Paper", "Code", "Download poster (PDF, 2.4 MB)", "Copy"), never "Click here" or "Learn more". One action keeps one name across the page, every button uses one capitalisation style, and each label fits one line at 360 px.

### Colour and contrast

- Text meets WCAG AA (4.5:1, or 3:1 for large text) on every background it sits on, including tinted bands and pills. Decorative accent colours are never used for text.

## Part 2: The bundled template

Class names and values are in [style-fidelity.md](style-fidelity.md). The template's comments mark each optional block.

### Columns and bands

- Every section uses `.container.is-max-desktop` (960 px). The centered reading column is `.columns.is-centered.has-text-centered > .column.is-four-fifths` (Abstract, YouTube); everything else is full width. `.measure` caps paragraphs at 768 px.
- Sections alternate plain and tinted (`section.section.is-light`). Keep the alternation when you delete optional blocks: two tinted bands in a row read as one section.
- The template left-aligns justified text below 768 px and scales the title down on phones. Hyphenated title terms go inside `<span class="nowrap">`.

### Header

- Venue or status: `.publication-venue` (a pill). Award: the commented `.publication-awards` line, used only for a verified award of any kind (best paper, thesis prize, department award). It is a quiet warm pill in the venue pill's shape with an optional trophy, award, or medal icon; keep the text short enough for one line at 360 px, and put the details in the abstract or a sentence below, not in the pill. Re-theming overrides `--award-color`, `--award-background`, `--award-border`, keeping 4.5:1. A full re-theme (dark, a custom accent) is a token override block only; see "Re-theming" in style-fidelity.md.
- Equal contribution: `*` marks after the names and the `.eql-cntrb` note; delete both together.
- Button icons are inline SVG from [icons.md](icons.md); a button deleted takes its icon with it.
- **More Works** (optional) sits in the page flow above the title. List only the user's own verified projects; delete the block otherwise.

### Carousels

- Use a carousel for a set of comparable items (qualitative results, scenes, clips), not for the key result or the method figure, which stay inline.
- `static/js/index.js` drives every `[data-carousel]`; no library. One slide at a time, off-screen slides `inert`, labelled buttons and dots, arrow keys and swipe, slides stack without JavaScript.
- Rotation is off. Add `data-autoplay="6000"` only when the user asks for rotation: a pause button appears, rotation stops on hover, focus, and while the figure viewer is open, and never starts under reduced motion.
- Image slides use `<figure class="carousel-card">` with a `<figcaption>`; add `data-zoom` to images readers will inspect. Give every image in a carousel the same aspect ratio, or crop to one: the carousel takes the height of its tallest slide, so a shorter image leaves a blank gap under it.
- Video slides hold short muted clips without `autoplay`; the script plays the current slide's clip only while the carousel is on screen.

### PDF poster

- The poster block embeds the PDF with a titled `<object>`, an inner link as fallback, and a download button that states the file size. Below 769 px only the link and button show.
- The full-page screenshots show the embed blank; `audit.mjs` saves a separate `page-<width>-pdf<N>.png` of each visible embedded PDF, so check that one, and confirm it loads in the live preview. A poster PNG preview, if the materials have one, may go in the teaser or results instead, but not both.

### BibTeX

- Show the citation whenever the project has one. Keep the copy button: it reports "Copied" or "Copy failed" and announces the result through the `role="status"` region. Keep the `pre` focusable.
- For work without a venue, use the entry the materials give (often `@misc` or `@unpublished`); do not invent a booktitle.

### Contents menu, back to top, and footer

- The `.page-nav` block is one floating pill: a Contents button that opens a menu of the page's sections, and back to top. `index.js` builds the list from the `h2` headings (no list to maintain); with fewer than three headings it keeps only back to top. Keep it when the page is long or has many sections (about five or more, or when a reader would scroll several screens to find one); delete the whole block when the page is short enough to scan.
- It appears after the header is scrolled past. On phones it is icon-only. Wherever it would sit over the text column (phones, tablets, narrow windows) it steps aside while the reader scrolls down, so it does not cover text being read; it returns on scroll up and at the end of the page.
- Behaviour to keep: real buttons with `aria-expanded`/`aria-controls`; Esc closes the menu and returns focus to the button; the current section carries `aria-current`; reduced motion removes the fade and the smooth scroll. Colours are theme tokens, so a dark or custom-accent re-theme needs no extra CSS.
- Keep the footer credit to both templates and the CC BY-SA 4.0 link. Add a line for the page's own content licence or a disclaimer only when the user gives one.

### Figure viewer

`static/js/figure-viewer.js` with `static/css/figure-viewer.css`. Add `data-zoom` to an `<img>`; the script wraps it in an accessible button and builds the dialog. Optional attributes: `data-zoom-src` (larger file), `data-zoom-title` (short title; defaults to the alt text), `data-zoom-caption` (caption text). Otherwise the caption comes from the enclosing `<figure>`'s `<figcaption>`, else a caption-like element in the nearest carousel slide or `[data-zoom-context]`.

Behaviour (do not reimplement): light backdrop; the figure grows from its page position; fit never exceeds 100 %; wheel and trackpad pinch zoom around the cursor; drag to pan; pinch and double-tap on touch; `+`, `-`, `0`, and arrow keys; zoom controls appear only for figures larger than the screen; the caption bar floats so zoomed figures run to the screen edges; reduced motion is respected. It dispatches `figure-viewer:open` and `figure-viewer:close` on `document`, and returns focus to the image, or to its carousel when the image is no longer visible.

## Pre-delivery checklist

Run `node scripts/audit.mjs <url>` and fix every failure. Then confirm on the screenshots it saves (the screen-height slices at 1440 and 375 px, and the full-page shot at 768 px), and in the live preview:

- [ ] Within each section, one left edge per column; no indented block under a full-width grid.
- [ ] Side-by-side teaser media share one height; no letterboxing.
- [ ] The method or architecture figure, if the project has one, is visible without opening a disclosure or a carousel.
- [ ] No image used twice; local video posters opened and not blank or black.
- [ ] One corner treatment for comparable media.
- [ ] No orphaned single word on the title or headings at 375 px.
- [ ] Tinted and plain bands still alternate after optional blocks were deleted.
- [ ] Each carousel steps forward and back, shows no blank gap under any slide, and does not rotate unless asked.
- [ ] Citation, if the project has one, shown as a visible BibTeX section; Copy works.
- [ ] Every zoomable figure opens, zooms, and closes; focus returns to it.
- [ ] Local videos seek in the preview (serve with `scripts/preview_server.py`); embedded YouTube and PDF poster load in the preview.
- [ ] No personal data, unreleased data, or harmful text in text, images, or video frames.
- [ ] `scripts/unused_assets.py` reports nothing to remove.
- [ ] `scripts/check_numbers.py` reports no unmatched numbers, or each one is traced to a stated derivation.
- [ ] `scripts/check_links.py` reports no link outside the materials (or each one came from the user and is passed with `--allow`) and no empty or placeholder link.
