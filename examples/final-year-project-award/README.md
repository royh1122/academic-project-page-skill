# Final year project with a verified award

**Materials:** kit [`eval-kit/kits/V3`](../../eval-kit/kits/V3) (fictional, generated). It contains:

- an 18-page report PDF with images and a bibliography
- a captioned explainer video, plus silent comparison loops
- a tracking GIF and an anamorphic dashboard capture
- an award letter, and a competition short paper that says "finalist"
- private repository READMEs, an `authors.json`, and raw user-study data with personal details

**Prompt:**

> Make a project page for our completed final year project "Quillwave: Sparse-Sensor Reconstruction of Synthetic Ripple Fields" by Ada Placeholder, Ben Example and Cleo Sample, supervised by Dr. Dana Specimen (Example University (fictional), Department of Imaginary Sciences). It received the Best Final Year Project Award 2026 from the department; the letter is in awards/. Buttons: Report and Video only. Do not link the repositories in repos/, they are private. Personal pages are in authors.json and are verified. Put the page in docs/.

Built in one run by a fresh agent with the skill. No edits afterwards.

![Header and teaser at 1440 px](./hero-desktop.jpg)

<img src="./hero-phone.jpg" alt="Header at 375 px" width="300">

## What the agent did

- **Award:** the award line is taken word for word from the letter. Nothing was added from the "finalist" short paper or from an award wish in the meeting notes.
- **Buttons and links:** Report and Video only. Ada and Ben link to the pages in `authors.json`; Cleo is plain text. There are no repository links.
- **Video:**
  - The explainer has controls, `preload="none"`, the kit's poster, a captions track and a transcript. It does not autoplay.
  - The silent loops autoplay muted and are paused for visitors who prefer reduced motion.
- **Left out:**
  - The dashboard capture, because it shows an operator badge and a licence plate.
  - The raw survey data; only the permitted averages appear.
  - The duplicate image copies.
- **Numbers:** only the final run's numbers. `check_numbers.py` matched all 81 numbers on the page to the sources.
- **Hand fixes after looking at screenshots:** kept "2025–2026" together on phones, and changed the limitations list into paragraphs.

**Gate:** `audit.mjs` page audit and typography pass, with no warnings. `unused_assets.py` found nothing to remove. A scripted check confirmed figure zoom, the carousel, video seeking and the copy button.

## Compared with no skill

The same prompt to a fresh agent without the skill also handled the award, links and personal data correctly. The differences are in presentation and checking:

- **Figures:** the dense results figure is unreadable inline, and no figure can be enlarged.
- **Extra elements:** metric cards at the top of Results; three loops at full column width.
- **Video:** the explainer uses `preload="metadata"`, and video seeking was never tested.

![Full pages, with and without the skill](./full-page-comparison.jpg)
