# Changelog

Versions match `metadata.version` in `skills/academic-project-page/SKILL.md`. Development history before the first release is not included.

## 1.1.0

**Page and template**

- **Teaser shows the main finding:** the visual a visitor would most want to see first, in whatever form the project has it (a result image or plot, a demo clip, a qualitative example, a screenshot of the working system). The method diagram is the teaser only when the method itself is the contribution or nothing else reads at phone width.
- **Contents menu:** the optional back-to-top button is replaced by a floating Contents and back-to-top pill. It builds its list from the page's `h2` headings, marks the current section, closes with Esc, and follows re-themed colours. It appears after the header and steps aside while the reader scrolls down wherever it would cover the text. Keep it on long pages; delete it on short ones.
- **Award style:** the award line is a quiet warm pill in the venue pill's shape with an optional trophy icon, instead of a red alert-style box.
- **Acknowledgments:** a new optional block for advisors who are not authors, funding, and data or compute providers.
- **Re-theming by tokens:** every colour in `index.css` and `figure-viewer.css` comes from a palette token, with new tokens for text on accent fills (`--on-primary`), buttons, links, strong text and the award. A dark theme or a custom accent is a `:root` override block only; `style-fidelity.md` has the recipe. The default look is unchanged apart from the figure viewer's greys, which now match the palette.

**Content rules**

- Give each main part of the work comparable depth, in proportion to the sources.
- The byline lists authors only; an advisor who is not an author goes in Acknowledgments by default, in the user's wording.
- An award is verified when the awarding body says the work received, won, or was selected for it; a finalist, shortlist, nomination, or hope is not. Ambiguous wording: show nothing and ask.

**Checks**

- **Interaction check:** `audit.mjs` drives the page with real key presses and clicks: zoomable figures (open, caption, zoom, Esc, focus return), carousels (buttons, arrow keys, inert slides, dots), the BibTeX copy button, the contents and More Works menus, and a Tab pass for visible focus and traps. It tests only the components a page has.
- **Readable screenshots:** besides the full-page shots, the audit saves screen-height slices at 1440 and 375 px (`page-<width>-NN.png`, `--max-slices`), and a viewport shot of each embedded PDF (`page-<width>-pdf<N>.png`), which full-page shots leave blank.
- **New audit checks:** a title that breaks inside a hyphenated term fails; a title ending in one word on its own line, a blank or near-black video poster, and a numeric table column aligned left are warnings.
- **Reporting:** a report names any screenshot or check that was skipped.
- `check_numbers.py` reads PDFs with `pdftotext` when PyMuPDF is not installed, and reads factors written with a trailing x ("1.36x") in sources.

**Evals and examples**

- A second Polish and Audit fixture, `flawed-v2`, with ten defects that mostly show only when looking at the page (evals 9 and 10). The answer keys expect a result teaser for the fictional kit.
- Examples rebuilt from fresh single runs on 1.1.0.

**Distribution**

- Installable as a Claude Code plugin: `/plugin install academic-project-page --marketplace royh1122/academic-project-page-skill` (`.claude-plugin/`).
- README: a live demo, a before/after clip, a quick start, how the skill differs from the template, how it is tested, a showcase section and an FAQ. Issue templates for bugs and showcase pages.
- `eval-kit/README.md` reports the 1.1.0 results.

## 1.0.1

- `preview_server.py` refuses a port that another server is still listening on, instead of binding it alongside (Windows) and leaving requests to reach the old server. It exits with a message naming the port.
- `audit.mjs` fails at once when the page does not load (HTTP error or no server), instead of auditing the server's error page and reporting a pass.

## 1.0.0

First release.

- **Template:** built on the Academic Project Page Template (itself adapted from Nerfies) with its defects fixed:
  - unclosed `<main>` and duplicate ids
  - headings before the `h1`
  - unlabelled controls and untitled embeds
  - text colours below 4.5:1
  - carousel autoplay with no pause control, and exposed clones
  - motion that ignored reduced-motion preferences
  - floating controls covering content on phones
  - unused jQuery, Adobe View SDK and bulma-slider
  - a JSON-LD licence that contradicted the page
- **Components** (each optional block delete-whole): head metadata, teaser, abstract, method figure, image and video carousels, YouTube (privacy-enhanced), results tables, PDF poster, BibTeX with an announced copy button, More Works, and a footer crediting both templates.
- **Theme check:** `check_style.js` compares rendered typography with `references/theme-profile.json`, including the font face Chrome actually rendered.
- **Audit** (`audit.mjs`, zero-install, installed Chrome), which checks:
  - resources and placeholders
  - headings, accessible names and iframe titles
  - contrast and synthesized bold
  - overflow, left edges, letterboxing
  - repeated images and corner radii
  - video posters, dimensions and seeking
  - a reduced-motion pass

  It saves screenshots at 375, 768 and 1440 px.
- **Other tools:**
  - `preview_server.py` serves under a repository subpath with HTTP range support.
  - `check_numbers.py` compares every number on the page with the sources.
  - `unused_assets.py` lists static files the page no longer references.
- **Figure viewer:** zoom around the pointer, pinch and keyboard control, caption from the figure, focus returned on close. It also works from carousel slides, which pause while it is open.
- **Evals and examples:**
  - A fictional, generated evaluation kit with three project variants, a flawed-page fixture and trap answer files.
  - 8 evals on that kit.
  - Examples from graded runs, each compared with a no-skill baseline.
