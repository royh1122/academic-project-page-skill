---
name: academic-project-page
description: Use when building, polishing, or auditing an academic project website - a research paper page, thesis or final-year project page, course project page, or demo page hosted on GitHub Pages, including pages based on the Academic Project Page Template or Nerfies. Also use when the user asks to "make a website for my paper", "create a project page", put a paper or project online with its figures, videos, poster, and BibTeX, or says an existing project page looks off, unpolished, or broken (fonts, alignment, videos that will not seek, carousels, images, links).
metadata:
  version: "1.4.0"
  author: "Roy Huang"
  license: "MIT AND CC-BY-SA-4.0"
---

# Academic Project Page

Turn a project's materials into an accurate, polished project page on the bundled template: the look of the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template) (adapted from [Nerfies](https://nerfies.github.io/)) with its accessibility, motion, and layout defects fixed. **Keep the bundled theme** unless the user asks for another look; their explicit design requests always win, and a re-theme is a `:root` token block ("Re-theming" in style-fidelity.md).

## Choose the path

| The request | Path |
| --- | --- |
| A new page from papers, reports, repositories, or media | **Build** |
| An existing page that looks off or needs finishing | **Polish**: fix defects only; keep copy, sections, links, and look, whatever its theme; name every change |
| "Is it ready?", "check it", "review it", no edits wanted | **Audit**: run the gate, look, report findings by priority; edit nothing |

## Tools

`<skill>` is this skill's folder. Run scripts as black boxes; read their source only if one fails in a way its output does not explain.

| Read or run | When |
| --- | --- |
| `template/index.html`, `static/` | Build: copy, then adapt. The template's opening comment lists its optional blocks. |
| [references/layout-polish.md](references/layout-polish.md) | Before arranging media, and in every Polish: alignment, teaser, figures, video, carousels, header, the pre-delivery checklist |
| [references/style-fidelity.md](references/style-fidelity.md) | Before changing any CSS |
| [references/icons.md](references/icons.md) | Before adding or changing an icon |
| `python <skill>/scripts/preview_server.py --root <site> --base <repo-name>` | Every path: serves the page under its repository subpath, with video seeking. Omit `--base` for a user or organization site. |
| `node <skill>/scripts/audit.mjs <url>` | The gate. Needs Node 22+ and an installed Chrome, Edge, or Chromium; `--help` for options. |
| `python <skill>/scripts/check_numbers.py <site>/index.html <sources>` | Any page that states results. Pass the files the numbers came from, not the whole repository: a large pool matches wrong numbers by coincidence. |
| `python <skill>/scripts/check_links.py <site>/index.html <sources> [--allow <url>]` | Every page. Pass all the materials (with none, it lists the links as unverified), and `--allow` only links the user gave in the chat, never one to quiet the check. |
| `python <skill>/scripts/unused_assets.py <site>` | Before reporting a Build or Polish. |

## Build

1. **Read the materials:** READMEs, reports, drafts, citation files, figures, posters, recordings. Extract title, authors and affiliations, abstract, links, visuals, and citation metadata. Separate reported results and intended capabilities from demonstrated deployment. When numbers disagree, use the latest final run and say which source you followed. Check each claim you reuse from captions, notes, or drafts against the data (a trend's direction, "best"); correct or drop one the data contradicts, and say so.
2. **Show only what the sources verify.**
   - Every external link (paper, code, DOI, arXiv, dataset, video, personal page) comes from the materials or the user; never complete one from a pattern such as a likely repository name. Authors without a verified personal URL are plain text.
   - A target venue, LaTeX template, author kit, or "potential submission" is not a venue; use the user's own status wording.
   - An award is verified when the awarding body says the work received, won, or was selected for it; a finalist, shortlist, nomination, candidacy, or someone's hope is not. When the wording is ambiguous, show nothing and ask, quoting it.
   - Omit what is unavailable and say so; never invent arXiv links, dataset releases, venues, awards, or metrics. Ask only for essential details that cannot be inferred, and honor an existing plan or review boundary without asking again.
3. **Keep sensitive data off the page**, even when the materials hold it: personal information (names, e-mails, phone numbers, faces, badges, plates, in images and video frames too), private or unreleased data, and harmful text (toxic examples, working attack strings, credentials). Describe such material in aggregate; crop or omit media that show it.
4. **Write a page brief** in your working notes, never on the page: the audience, the one-sentence takeaway, what the first screen must show, the section order, and why this teaser.
5. **Fill the template.** Copy `template/` and the `static/` files the page needs, keeping the theme (style-fidelity.md). Fill the title, authors, affiliations, resource buttons, a teaser with a short caption, the abstract, and sections chosen by the material; arrange media by layout-polish.md. Delete each `BEGIN optional` block the project lacks, whole.
   - **Coverage:** first list the work's main parts from the sources (each main chapter, system component, experiment, or study), then give each depth in proportion to the sources: never one in a sentence while another gets a section. A part whose code is private is still part of the work; show it from the report.
   - **People:** the byline lists authors only. A supervisor or advisor who is not an author goes in Acknowledgments, in the user's wording, unless the user asks for a labelled line.
   - **Contents menu:** keep it on long pages with many sections; delete it whole on short ones.
   - **Then compare the page with the brief:** is this what you would produce for any paper? If so, the teaser, first screen, or section order is not yet following this project.
6. **Fill the head** to match the page: title, description, Open Graph and Twitter text, `citation_*` tags, JSON-LD. Use the page URL (canonical, `og:url`, JSON-LD `url`) only when it is known, from the user or the repository's Pages settings; otherwise delete those lines and say so. Add a social image only when a real 1200 × 630 image exists.
7. **Finish the files.**
   - Paths are document-relative (`./static/...`), external links absolute.
   - Video by content: short silent loops autoplay muted; anything with audio or longer than about 30 s gets controls, `preload="none"`, captions, and a transcript (layout-polish.md, Video).
   - Delete the figure viewer files when no image uses `data-zoom`, and `reduced-motion.js` when nothing autoplays.
   - Remove every `[INSERT ...]` token and unused static file, and delete your own helper scripts and temporary files.
   - Keep the footer credit to both templates with the CC BY-SA 4.0 link. No analytics unless asked.

## Gate, look, report

Passing the gate means nothing measurable is wrong, not that the page is good. Do every step.

1. **Gate.** From the project folder, serve with `preview_server.py` and run `audit.mjs`, then `check_numbers.py` and `check_links.py`.
   - Screenshots go to `.page-audit/`. Never share an `--out` folder with another run, and delete the folder before reporting.
   - Fix every failure. Treat every warning as a defect unless you can defend it in one sentence, which goes in the report. Rerun until nothing fails.
   - For a requested redesign, or a Polish of a page in another theme, pass `--skip-style` and say so.
   - If a sandbox stops the browser from starting, the audit says so: ask the user to approve running it outside the sandbox instead of skipping the gate. Never set `PAGE_AUDIT_NO_SANDBOX` yourself; turning off Chrome's sandbox is the user's choice.
2. **Look.** Open every screenshot the audit saved, every slice at both widths, and work through the pre-delivery checklist; a problem visible in a screenshot is real, whatever the code says. Labelling a slice "not run" is for one the audit could not make, not one you skipped.
   - Read the screen-height slices (`page-<width>-NN.png`, 1440 and 375 px) in order: only they are legible. The full-page shots and 768 px show rhythm.
   - Embedded PDFs are blank in full-page shots, so open each `page-<width>-pdf<N>.png`; check YouTube embeds in the live preview.
   - Batch the fixes from one look before looking again; three rounds at most.
3. **Interact.** The audit drives figures, carousels, the copy button, menus, and a Tab pass. Judge what it cannot: a zoomed figure is sharp and readable, a carousel video plays, focus rings are visible. If the audit could not run, do those mechanics by hand.
4. **Report.** In Build and Polish, report only after a gate run with no failures (in a scoped Polish, none in the named part) and after opening every one of its screenshots (in a scoped Polish, those showing the named part). Give the preview URL, the gate result with any defended warnings (each cited by its `[id]`), what you checked by looking, omitted resources, sample content still to replace, and what you could not check. Never claim a check you did not run:
   - Label each check (audit, interaction check, `check_numbers.py`, `check_links.py`, `unused_assets.py`, each set of screenshots) as passed, ran with findings (name them), or not run (say why). A gate that could not start, an empty result, or a screenshot you did not open is "not run", never a pass.
   - When the gate could not run at all, open the report with `DEGRADED: <reason>`, then the hand checks.
   - Results go stale: any edit after the last gate run invalidates it, so rerun before reporting. A blank, half-loaded, or wrong-width screenshot is not evidence; retake it.
   - Label what you could not verify as unverified instead of leaving it out: a number traced to no source, a link the user did not give, an optional block kept without matching material.

   Preview approval does not authorize a push, publication, or repository visibility change.

## Polish and Audit

- **Before:** run the gate on the untouched page with `--out .page-audit/before`; the report gives its failure and warning counts beside the final run's.
- **Scope:** when the user names a part ("polish the teaser", "fix the videos"), touch only that part and list other defects instead of fixing them; failures outside it do not hold back the report. Otherwise fix the gate's findings and what the screenshots show, nothing more.
- **Pasted feedback:** reproduce each item on the live page (a screenshot or an interaction) before fixing it. Fix what reproduces; report what does not, with what you saw. Still run the whole gate.
- **Triage:** broken or blocked content (dead links, missing media, unreadable text), then accessibility, then layout and consistency, then cosmetics. Fix at the narrowest level: an attribute or one rule, not a restyle.
- **Audit findings:** rank each P0 (blocks publishing: broken or missing content, a false or unverified claim, private data), P1 (accessibility or interaction), P2 (visible layout or consistency), or P3 (cosmetic), and give its fix path: Polish, ask the user (needs a fact, file, or decision), or a template block. Questions to the user go last.

**Before you finish**, check the mode's promise. Build: every number traces to a source or a stated derivation, every external link to the materials or the user, and every omitted resource is named. Polish: a diff shows nothing changed outside the defects you name. Audit: no project file was edited, and `.page-audit/` is deleted.

## Common mistakes

| Mistake | Instead |
| --- | --- |
| Metric counters, icon "contribution" cards, numbered steps, eyebrow labels, badges, or a "key contributions" box on content without that structure; new accent colours | The template's sections, figures, and paragraphs; numbers only for a real sequence |
| A dense multi-panel figure or the method diagram as the teaser when a legible outcome visual exists | The main finding as the teaser (layout-polish.md, Teaser) |
| Teaser media in fixed-height boxes with `object-fit: contain` | Grid columns proportional to the media's aspect ratios |
| The method figure or the key result hidden in a disclosure or on a later carousel slide; one image in two sections | Both inline; each image once |
| "Coming soon" or greyed-out buttons for a paper, code, or dataset that does not exist | No button; a status line if the user gave one |
| More Works filled with guesses | Only the user's verified projects, or delete the menu |
| In a page you build: `<i class="fa-...">` icons, a custom lightbox, or a slider library | The SVG icons in icons.md, `data-zoom` with the bundled viewer, the bundled carousel. An existing page's working icon font or library is not a defect |
| `python -m http.server`, then "videos can't seek" | `preview_server.py` |
| Polishing by restyling the page | Defect fixes only; a redesign only on request |
