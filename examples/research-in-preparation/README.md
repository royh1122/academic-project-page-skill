# Research in preparation, no paper or links

**Materials:** kit [`eval-kit/kits/V2`](../../eval-kit/kits/V2) (fictional, generated). It contains:

- a two-page summary, figures and captions
- result tables and silent comparison loops
- an experiment log with superseded draft numbers
- a submission plan with a target-venue author kit
- raw user-study data containing personal details and insults
- a GIF and an anamorphic screen capture

**Prompt:**

> Make a project page from the materials in this folder. Author: Ada Placeholder, Example University (fictional), Department of Imaginary Sciences. Individual project. Present it as research in preparation. No paper yet and no public links. Put the page in docs/.

Built in one run by a fresh agent with the skill. No edits afterwards.

![Header and teaser at 1440 px](./hero-desktop.jpg)

<img src="./hero-phone.jpg" alt="Header at 375 px" width="300">

## What the agent did

- **Status:** a "Research in preparation" pill, the user's own wording. The target venue in `submission/` is not presented as a venue.
- **No resource buttons**, and no "coming soon" placeholders.
- **Caption fix:** it noticed that a source caption claims the gap "grows with fewer sensors" while the sweep shows the opposite. It removed the claim.
- **Personal data:** only the permitted user-study averages appear. The screen capture with an operator badge is left out.
- **Layout:**
  - method figure inline and zoomable, with its empty margins cropped
  - the dense results figure zoomable in Results
  - the remaining loops in a carousel that does not rotate
- **Metadata:** filled. The page-URL lines were deleted because the address isn't known.

**Gate:** page audit and typography pass, with no warnings. `check_numbers.py` left one unmatched number, the licence version "4.0".

## Compared with no skill

The baseline was careful with content too: no venue, no stale numbers, no personal data. Its weaknesses were in presentation:

- greyed "Paper: in preparation" and "Code: not yet public" labels in the header
- metric cards
- figures that can't be enlarged
- one section with two left edges

![Full pages, with and without the skill](./full-page-comparison.jpg)
