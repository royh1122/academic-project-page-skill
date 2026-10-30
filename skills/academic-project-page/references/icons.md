# Icons

The template draws its icons as inline SVG, so no icon font or script is loaded. The `icon-svg` class in `index.css` sizes an icon to the text and colours it with `currentColor`. An icon goes inside the `<span class="icon" aria-hidden="true">` of a button, or before the text of the award line; delete it with the element that holds it.

**To add one,** read only its file, `references/icons/<name>.svg` (one line each), and paste that line in. The set:

- **Resource buttons:** `file-pdf` (Paper PDF), `arxiv` (arXiv), `file-lines` (Supplementary material, report), `github` (Code on GitHub), `gitlab` (Code on GitLab), `code` (Code elsewhere), `database` (Data), `table` (Results tables, benchmark), `youtube` (Video on YouTube), `video` (Video file), `person-chalkboard` (Slides, talk), `image` (Poster image, gallery), `book` (Thesis, book), `graduation-cap` (Thesis, course), `laptop-code` (Live demo, notebook), `globe` (Website), `file-zipper` (Archive, model weights), `quote-left` (Citation), `orcid` (ORCID), `link` (Any other link).
- **Template parts:** `flask` (More Works button), `chevron-down` (More Works arrow), `chevron-up` (Back to top), `chevron-left` (Carousel previous (index.js)), `chevron-right` (Carousel next (index.js)), `play` (Carousel play (index.js)), `pause` (Carousel pause (index.js)), `xmark` (Close), `arrow-up-right-from-square` (External link in More Works), `list-ul` (Contents menu), `copy` (Copy BibTeX), `download` (Download poster or file), `trophy` (Award line), `award` (Award line (alternative)), `medal` (Award line (alternative)).

**An icon not in the set:** take it from Font Awesome Free 6.7.2, `https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/svgs/<solid|regular|brands>/<name>.svg` (names at fontawesome.com/icons, Free set). Delete its licence comment, add `class="icon-svg" aria-hidden="true"` to the `<svg>`, and paste it in. Without network access, use the closest icon in the set or none, and say so.

Never use `<i class="fa-...">`: no icon font is loaded, so it draws nothing, and the audit fails it. If the user asks for the full Font Awesome library, add its stylesheet as they ask.

The page keeps one licence comment in its `<head>` (Font Awesome Free icons are CC BY 4.0; the arXiv icon is from Academicons, SIL OFL 1.1). Keep it while any of these icons is on the page.
