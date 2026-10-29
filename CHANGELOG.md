# Changelog

Versions match `metadata.version` in `skills/academic-project-page/SKILL.md`. Development history before the first release is not included.

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
