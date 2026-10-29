# Academic Project Page

**An agent skill that turns your paper, figures, and videos into a polished project page for GitHub Pages.**

Point your coding agent at a folder of project materials (a paper or report PDF, figures, result tables, videos, a poster, BibTeX) and it builds a responsive project page in the style of the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template) and [Nerfies](https://nerfies.github.io/). It then checks the page in a real browser before handing it back. The same skill also polishes an existing page or audits one before you publish.

[![CI](https://github.com/royh1122/academic-project-page-skill/actions/workflows/validate-skill.yml/badge.svg)](https://github.com/royh1122/academic-project-page-skill/actions/workflows/validate-skill.yml)
[![Agent Skill](https://img.shields.io/badge/format-Agent_Skill-blue.svg)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

![A paper project page built by the skill](./examples/paper-full-links/hero-desktop.jpg)

## Install

```bash
npx skills add royh1122/academic-project-page-skill
```

Or copy the skill folder into your agent's skills directory:

```bash
git clone https://github.com/royh1122/academic-project-page-skill.git
cp -r academic-project-page-skill/skills/academic-project-page ~/.claude/skills/
```

It works with Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, and any agent that reads `SKILL.md` skills.

**Requirements:**

- Python 3 and Node 22 or newer
- an installed Chrome, Edge, or Chromium, for the browser checks
- ffmpeg, for converting GIFs and recordings

## Use

Ask for a page and say what only you know: authors, verified links and awards, and what may be public.

> Make a project page for our paper "…" by …, accepted at …. Paper: https://…, code: https://…. The materials are in this folder. Put the page in `docs/`.

> Our project page in `docs/` looks a bit off. Can you polish it? Don't change the content.

> Is the page in `docs/` ready to publish? Just tell me what's wrong.

## What it does

**Build.** The agent reads the materials and fills the template with what they support:

- title, authors and affiliations
- the venue or status line, and resource buttons
- a teaser, the abstract, and the method figure
- results tables, image and video carousels, an embedded PDF poster
- BibTeX with a copy button
- search and social metadata

Optional blocks the project lacks are removed rather than left as placeholders.

**Content rules.** The page states only what the sources verify:

- A target venue or a finalist listing does not become an acceptance or an award.
- Draft numbers are not used.
- Claims in reused captions are checked against the data.
- Personal data, unreleased data, and harmful text stay off the page, including faces, badges, and plates in video frames.

**Media.**

- Short silent loops autoplay muted and stop for visitors who prefer reduced motion.
- Videos with audio get controls, captions, and a transcript.
- GIFs and anamorphic recordings are converted to square-pixel MP4.
- Dense figures open in an accessible zoom viewer.

**Checks.** Before reporting, the agent:

- serves the page under its repository subpath, with video seeking working
- runs a browser audit
- checks every number on the page against the source files
- reviews screenshots at 375, 768, and 1440 px

The audit covers:

- missing files and leftover placeholders
- heading order, accessible names, and contrast
- fonts rendered with synthesized bold
- horizontal overflow, alignment, and letterboxed media
- repeated images
- video posters and seeking
- motion under reduced-motion settings
- the theme's typography

**Polish and Audit.** Polish fixes defects without changing content and reports the audit before and after. Audit reports problems by priority and edits nothing.

## Examples

Each example was built in one run from a fictional project in the [evaluation kit](./eval-kit/), then compared with the same prompt given to an agent without the skill.

| Example | Materials |
| --- | --- |
| [Accepted paper](./examples/paper-full-links/README.md) | Paper and poster PDFs, captioned explainer video, comparison loops, figures, tables |
| [Research in preparation](./examples/research-in-preparation/README.md) | Summary PDF, figures, tables, a draft submission plan, raw study data with personal details |
| [Final year project with an award](./examples/final-year-project-award/README.md) | Report PDF, award letter, explainer video, private repositories, author pages |

Results with and without the skill are in [eval-kit/README.md](./eval-kit/README.md#results-for-v100).

## What's inside

```text
skills/academic-project-page/
├── SKILL.md                    workflow: build, polish, or audit
├── references/
│   ├── layout-polish.md        layout rules and the pre-delivery checklist
│   ├── style-fidelity.md       theme: type scale, palette, spacing, components
│   └── theme-profile.json      expected rendered values for the typography check
├── template/index.html         page template with optional blocks
├── static/                     Bulma, Font Awesome, theme CSS, carousel, figure viewer, reduced-motion script
├── scripts/
│   ├── audit.mjs               browser audit and screenshots, using the installed Chrome
│   ├── preview_server.py       local preview under a repository subpath, with video seeking
│   ├── check_numbers.py        numbers on the page against the source files
│   └── unused_assets.py        static files the page no longer uses
└── evals/evals.json            eight evals
eval-kit/                       fictional projects, generator, and a flawed-page fixture for the evals
examples/                       example runs with screenshots
```

## Privacy

Pages are built and previewed locally. The agent publishes, pushes, or changes repository visibility only when you ask. The template loads the Inter font from Google Fonts; YouTube embeds contact YouTube. There are no analytics.

## License

- **Skill and tooling:** [MIT](./LICENSE).
- **Bundled template:** adapted from the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template) by Eliahu Horwitz and [Nerfies](https://github.com/nerfies/nerfies.github.io) by Keunhong Park et al., both [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Generated pages keep the footer credit to both.
- **Evaluation kit:** [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
