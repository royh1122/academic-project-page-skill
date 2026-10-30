---
name: academic-project-page
description: Use when building, polishing, or auditing an academic project website - a research paper page, thesis or final-year project page, course project page, or demo page hosted on GitHub Pages, including pages based on the Academic Project Page Template or Nerfies. Also use when the user asks to "make a website for my paper", "create a project page", put a paper or project online with its figures, videos, poster, and BibTeX, or says an existing project page looks off, unpolished, or broken (fonts, alignment, videos that will not seek, carousels, images, links).
metadata:
  version: "1.1.1"
  author: "Roy Huang"
  license: "MIT AND CC-BY-SA-4.0"
---

# Academic Project Page

Turn a project's materials into a polished, accurate project page built on the bundled template: the look of the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template) (itself adapted from [Nerfies](https://nerfies.github.io/)) with its accessibility, motion, and layout defects fixed. **Keep the bundled theme by default.** A request for a project page authorizes adapting content and arranging media; it does not imply a new visual identity. The user's explicit design requests always win. A requested re-theme (dark, a custom accent) is a `:root` token override block only; see "Re-theming" in style-fidelity.md.

## Choose the path first

| The request | Path |
| --- | --- |
| A new page from papers, reports, repositories, or media | **Build** (all sections below) |
| An existing project page that looks off or needs finishing | **Polish**: run the gate first, fix defects only, keep copy, sections, links, and look (even when it is not the bundled theme); name every change. Polish never becomes an unrequested redesign. |
| "Is it ready?", "check it", "review it", no edits wanted | **Audit**: serve, run the gate, look at the screenshots, report findings by priority. Edit nothing. |

## Files

`<skill>` is this skill's folder. Run scripts as black boxes; read their source only if one fails in a way its output does not explain.

| File | Read or run it when |
| --- | --- |
| `template/index.html`, `static/` | Build: copy them, then adapt. The template's opening comment explains its optional blocks. |
| [references/layout-polish.md](references/layout-polish.md) | Before arranging media, and for every Polish: alignment, teaser, figures, video, carousels, poster, header, the pre-delivery checklist. |
| [references/style-fidelity.md](references/style-fidelity.md) | Before changing any CSS: the theme's typography, palette, spacing, and component rules. |
| `python <skill>/scripts/preview_server.py --root <site> --base <repo-name>` | Every path: serves the page under its repository subpath with working video seeking. Omit `--base` for a user or organization site. |
| `node <skill>/scripts/audit.mjs <url>` | The gate. Node 22+ and an installed Chrome/Edge/Chromium; installs nothing. `--help` for options. |
| `python <skill>/scripts/unused_assets.py <site>` | Before reporting a Build or Polish. |
| `python <skill>/scripts/check_numbers.py <site>/index.html <source files>` | Before reporting any page that states results. Pass the specific files the numbers came from (tables, logs, the paper), not the whole repository: a large pool matches wrong numbers by coincidence. PDFs are read with PyMuPDF or, failing that, `pdftotext`; if it notes neither is available, numbers found only in a PDF went unchecked. |
| `scripts/audit_page.js`, `scripts/check_style.js` | Only when using Playwright directly: `playwright-cli run-code --filename <file>`. `audit.mjs` already runs both. |
| `static/js/figure-viewer.js` + `static/css/figure-viewer.css` | When figures need close inspection: add `data-zoom` to the `<img>`. Never write another lightbox. |
| `evals/evals.json` | When changing this skill: rerun the evals and a no-skill baseline. |

## Build from supported project details

1. Inspect READMEs, reports, paper drafts, citation files, figures, posters, and recordings. Extract title, authors and affiliations, abstract, verified links, visuals, and citation metadata. Distinguish reported results and intended capabilities from demonstrated deployment. When numbers disagree between sources, use the latest final run and say which source you followed. Check every claim you reuse from captions, notes, or drafts against the data (a trend's direction, "best", "grows with"); correct or drop a claim the data contradicts and say so. `check_numbers.py` checks values, not claims.
2. Ask only for essential missing details that cannot be inferred. Omit unavailable optional resources and state the omission; do not invent arXiv links, dataset releases, venues, awards, or metrics. Render authors as plain text when no verified personal URL exists. A target venue, LaTeX template, author kit, or "potential submission" in the materials is not a venue; use the user's own status wording instead. The awarding body saying the work received, won, or was selected for an award verifies it; a finalist, shortlist, nomination, candidacy, or a team member's hope does not. When the wording is genuinely ambiguous, show nothing and ask, quoting the sentence. Honor an existing plan or review boundary without asking again.
3. Keep sensitive data off the page even when the materials contain it: personal information (names, e-mails, phone numbers, faces, badges, plates in images and video frames), private or unreleased data, and harmful or protected text (toxic examples, attack strings that work, credentials). Describe such examples in aggregate or by reference instead; crop or omit media that show them.
4. Copy the template and needed static assets. Keep the theme: Inter from the template's font request (it loads the 400 to 800 weights the CSS uses), the palette tokens in `index.css`, the 960 px column, and the section rhythm. Keep the bundle's accessible colours; check any new colour against `#f1f5f9`. Use ordinary figures and captions; see Common mistakes for what not to invent.
5. Populate the template: the centered title, authors, affiliations, and resource buttons; a teaser with a short caption; a readable abstract; and sections chosen by the project's material. Delete each `BEGIN optional` block the project lacks as a whole rather than leaving placeholders. Arrange media by the layout contract.
   - **Coverage.** List the work's main parts (each main chapter, system component, experiment, or study) from the sources and give each comparable depth, in proportion to the sources. Do not reduce one major part to a sentence while another gets a full section.
   - **People.** The byline lists authors only. An advisor or supervisor who is not an author goes in the template's Acknowledgments block by default, or on a clearly labelled line when the user asks for one, credited in the user's own wording. A co-author is an author.
   - **Contents menu.** Keep the template's contents block (a floating Contents and back-to-top pill that builds itself from the `h2` headings) on long pages with many sections; delete it whole on short pages.
6. Fill the head: title, description, Open Graph and Twitter text, `citation_*` tags, and JSON-LD, all matching the visible page. Use the page URL (canonical, `og:url`, JSON-LD `url`) only when it is known, for example from the user or the repository's Pages settings; otherwise delete those lines and say so. Add a social preview image only when a real 1200 × 630 image exists.
7. Use document-relative paths (`./static/...`), including video posters. Keep external links absolute. Keep the Font Awesome SVG JavaScript. Delete the figure viewer files when no image uses `data-zoom`, `reduced-motion.js` when nothing autoplays (no `video[autoplay]`, no `data-autoplay` carousel), and the Academicons stylesheet with the arXiv button.
8. Set video behaviour by content: short silent loops autoplay muted; videos with speech or audio, or longer than about 30 s, get controls, `preload="none"`, captions, and a transcript. Convert GIFs and re-encode recordings as the contract's Video section shows (square pixels). Pick each local poster frame by looking at candidates.
9. Remove every `[INSERT ...]` token, placeholder link, and unreferenced static file. Keep the footer crediting both the Academic Project Page Template and Nerfies with the CC BY-SA 4.0 link. Keep analytics off unless explicitly requested.

## Gate, look, report

Passing the gate means nothing measurable is wrong; it does not mean the page is good. Do all of these.

1. **Gate.** Serve with `preview_server.py` and run `node <skill>/scripts/audit.mjs <url>` from the project folder (screenshots go to `.page-audit/` there; never point `--out` at a folder another run may share, and delete it before reporting), then `check_numbers.py` against the result sources. If the agent runs in a sandbox that stops the browser from starting, the audit says so: request permission to run that command outside the sandbox (the user approves it) instead of skipping the gate. Never set `PAGE_AUDIT_NO_SANDBOX` yourself; it turns off Chrome's sandbox and is the user's choice. The audit checks resources, ids, headings, names, placeholders, contrast, synthesized bold, overflow, alignment, media, video seeking, embeds, and a reduced-motion pass. It then drives the page with real key presses and clicks (`Interaction check`): each zoomable figure, carousel, BibTeX copy button, contents menu, and More Works menu the page has, then one Tab pass for visible focus and traps; a page without these parts has nothing to check there. Fix every failure. Treat every warning as a defect unless you can defend it to the user in one sentence, and put that sentence in the report. Re-run until there are no failures. For a requested redesign or a Polish of a page in another theme, pass `--skip-style` and state the changed expectations.
2. **Look.** Open every screenshot `audit.mjs` saved and work through the contract's pre-delivery checklist. If a problem is visible in a screenshot, it is real, whatever the code says. The `page-<width>-NN.png` slices (1440 and 375 px, one screen each) are what is legible: open them in order, since a full-page shot shrinks until orphaned words and repeated bands vanish; the full-page shots (and 768 px) show overall rhythm. A page longer than the slice cap says so; rerun with `--max-slices`. Batch fixes from one look before looking again; three rounds at most. Headless screenshots leave YouTube embeds blank; check those in the live preview. Embedded PDFs are blank in the full-page shots, so `audit.mjs` also saves `page-<width>-pdf<N>.png` for each; open it too.
3. **Interact.** The audit has already done the mechanics (open, close and focus return of figures; carousel buttons, arrow keys, inert slides; copy status; menus; Tab pass), so only look at what it cannot judge: open one zoomed figure and check the enlarged image is sharp and readable, watch a carousel video play, and check that focus rings are visible against the page in the screenshots. Fix every Interaction failure and treat its warnings like the audit's. If the audit could not run, do the whole list by hand: open each zoomable figure, step through each carousel, press the BibTeX copy button, and tab through the page once.
4. **Report** only when the last gate run has no failures and you have opened every one of its screenshots and done step 3's looks; name any you skipped and why. Tell the user: the preview URL, the gate result and any defended warnings, what you checked by looking, omitted resources, sample content still to replace, and anything you could not check (no browser, no network). Never claim a check you did not run. Preview approval does not authorize a push, publication, or repository visibility change.

## Common mistakes

| Mistake | Instead |
| --- | --- |
| Hero metric counters, icon "contribution" cards, numbered step boxes, new accent colours | The template's sections, figures, captions, and paragraphs |
| Venue, award, dataset, or code link inferred from hopes, drafts, or a finalist listing | Only verified items; say what was omitted |
| An advisor or supervisor who is not an author listed in the byline | Authors only in the byline; the advisor in Acknowledgments in the user's wording |
| One major part of the work in a sentence while another gets a full section | A comparable share of the page for each main part, in proportion to the sources |
| Two teaser media in fixed-height boxes with `object-fit: contain` | Grid columns proportional to aspect ratios (contract, Teaser) |
| A paragraph or sub-heading indented under a full-width grid | One left edge per section column |
| Method figure hidden in a disclosure or a carousel; the same image in two sections | Method figure inline; each image once |
| The key result only on slide 3 of a carousel | The key result inline; carousels for sets of comparable results |
| Carousel rotation on by default, or a custom slider library | The bundled carousel; `data-autoplay` only when asked, which adds a pause button |
| A PDF poster in a bare iframe | The template's poster block: titled embed, download button, link-only on phones |
| Inter requested at 400 only; text in the decorative accent colours | The template's font request; text colours from the palette |
| `python -m http.server` preview, then "videos can't seek" | `preview_server.py` (range requests) |
| A custom lightbox with fit/actual-size buttons | `data-zoom` and the bundled figure viewer |
| Polishing by restyling the whole page | Defect fixes only; redesign only on request |
| "Coming soon" buttons for a paper or code that does not exist | No button; a status line if the user gave one |
| More Works filled with guesses | Only the user's verified projects, or delete the menu |
| No teaser, a dense multi-panel figure as the teaser, or the method diagram as the teaser when a legible outcome visual exists | A teaser showing the main finding in whatever form the project has it; the method diagram only when the method is the contribution or nothing else reads; dense figures in their results section |
