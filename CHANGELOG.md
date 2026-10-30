# Changelog

Versions match `metadata.version` in `skills/academic-project-page/SKILL.md`. Development history before the first release is not included.

## 1.2.0

**Reports you can trust**

- **Every check is labelled:** the report says which checks passed, which ran with findings, and which did not run and why. A check that could not start, an empty result, or a skipped screenshot is "not run", never a pass. When the browser check cannot run at all, the report opens with `DEGRADED: <reason>`.
- **Results go stale:** an edit after the last check run means running it again before reporting; a blank, half-loaded, or wrong-width screenshot is retaken, not counted.
- **Unverified items are named:** a number traced to no source, a link the user did not give, or an optional block kept without matching material is reported as unverified instead of left out.
- **Audit findings ranked P0 to P3** (blocks publishing, accessibility or interaction, layout, cosmetic), each with a way to fix it, and any question to the user last.

**Polish**

- **Scope:** "polish the teaser" touches only the teaser; other defects are listed, not fixed, and do not hold back the report.
- **Pasted reviewer notes** are reproduced on the live page before any fix; notes that do not reproduce are reported with what was seen, not "fixed".
- **Before and after:** the audit runs on the untouched page first, and the report gives both counts.
- **Triage order:** broken content, then accessibility, then layout, then cosmetics, each fixed at the narrowest level.
- **Before you finish:** a short final check per mode (Build: numbers and links traced, omissions named; Polish: nothing changed outside the named defects; Audit: nothing edited).

**Build and content**

- **External link check:** new `scripts/check_links.py` lists every external link on the page (buttons, embeds, meta tags, JSON-LD) and flags any found in none of the sources, plus empty and placeholder links. arXiv, DOI and YouTube links match on their identifier; links the user gives in the chat are passed with `--allow`. It runs in the gate beside `check_numbers.py`.
- **Page brief:** before filling the template, the agent writes three to five lines in its working notes (audience, takeaway, first screen, section order, why this teaser), then checks the result is not what it would produce for any paper.
- **Structure only where the content has it:** no numbered steps, eyebrow labels, badges, or "key contributions" boxes on content without that structure.
- **Button wording:** buttons say what they do or where they go, one action keeps one name, one capitalisation style.

**Repository**

- **CI checks the release files agree:** the version in `SKILL.md`, the Claude Code marketplace entry and the Codex plugin must match, every manifest must point at a real `SKILL.md`, and the frontmatter must parse without duplicate keys.
- **Evals 11 and 12:** a scoped Polish from pasted reviewer notes (one of which does not reproduce), and a build where the user asks for Paper, Code and Dataset buttons the materials cannot support. The audit and polish evals now expect P0-P3 findings, labelled checks and before/after counts.

## 1.1.1

- **Smaller plugin install:** the Claude Code and Codex plugins now install only the skill folder (1.7 MB) instead of a copy of the whole repository (eval kit, examples and README media, about 26 MB). Both marketplaces point at `./skills`; the Codex manifest moved to `skills/.codex-plugin/plugin.json`, and the Claude Code plugin's details live in its marketplace entry.
- **Codex plugin:** `skills/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`, so Codex installs it with `codex plugin marketplace add royh1122/academic-project-page-skill` and `codex plugin add academic-project-page@royh1122-skills`. **Tested with Codex:** the skill triggered on its own, Codex asked to run the browser audit outside its sandbox, fixed the contrast issue and missing video posters the audit found, and passed it on the rerun. Unattended runs (`codex exec`) cannot ask, so the browser check does not run there unless the user opts in (below).
- **Clear error inside an agent's sandbox:** when Chrome starts but its tab never answers (Chrome cannot start its own sandbox inside the agent's), the audit stops after 10 seconds and says to run it outside the sandbox, instead of exiting with only "unsettled top-level await". `SKILL.md` tells the agent to ask for that permission instead of skipping the check. A user running an agent unattended can set `PAGE_AUDIT_NO_SANDBOX=1` to run Chrome without its sandbox; the agent never sets it.
- **Interaction check no longer fails working zoom buttons:** it scrolled smoothly (the template's default) and could click before the page stopped moving, reporting "a click does not open the figure viewer" for figures further down the page. It now scrolls instantly.

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
