# Accepted paper with all links

**Materials:** kit [`eval-kit/kits/V1`](../../eval-kit/kits/V1) (fictional, generated). It contains:

- a paper PDF with its LaTeX source, and a poster PDF
- a captioned explainer video (it has an audio track), plus three silent comparison loops
- figures with captions, and result tables
- an acceptance e-mail, `links.json`, and `citation.bib`

**Prompt:**

> Make a project page for our paper "Quillwave: Sparse-Sensor Reconstruction of Synthetic Ripple Fields" by Ada Placeholder, Ben Example and Cleo Sample (Example University (fictional), Department of Imaginary Sciences), accepted at FCSV 2026. The materials are in this folder. Paper: https://quillwave.example.org/quillwave_fcsv2026.pdf, code: https://code.example.org/quillwave. Host the explainer video video/overview_explainer.mp4 with the page (no external video service). The comparison clips in results/loops are silent. Put the page in docs/.

Built in one run by a fresh agent with the skill (v1.1.0). No edits afterwards.

![Header and teaser at 1440 px](./hero-desktop.jpg)

<img src="./hero-phone.jpg" alt="Header at 375 px" width="300">

## What the agent did

- **Header:** a venue line confirmed by the acceptance e-mail, and Paper and Code buttons with the user's two links.
- **Teaser:** a silent comparison loop, linear interpolation beside the Quillwave reconstruction, so the page opens on the result. The other two loops are in a carousel, and the pipeline diagram is inline in Method.
- **Video:** the explainer has controls, `preload="none"`, a poster, captions and a transcript link.
- **PDF poster:** embedded with a download button, falling back to a link on phones.
- **Figures:** the dense results figure and the comparison grid are zoomable, with their empty margins cropped.
- **Caption fix:** it dropped a source caption's claim that the sweep data contradicts ("the gap grows with fewer sensors").
- **Left out:** an award a co-author hoped for in the meeting notes, a meeting attendee whose role the materials don't give, the authors' e-mail addresses, and the duplicate and single-scene images.

**Gate:** the first audit run failed because the title broke inside "Sparse-Sensor"; the agent kept the term together and re-ran. The page audit, interaction check and typography check then passed with no warnings. `check_numbers.py` matched 78 of 80 numbers; the other two are the poster's file size and the licence version.

## Compared with no skill

The baseline ran in the first evaluation round; it does not depend on the skill's version.

- **Invented address:** the baseline made up a hosting address for the page's link-preview tags.
- **Figures and layout:** metric tiles, figures that can't be enlarged, and loops without poster frames, which the audit warned about.
- **Video seeking:** never verified, because Python's simple server ignores range requests.

![Full pages, with and without the skill](./full-page-comparison.jpg)

The dark box in the Poster section is the embedded PDF, which headless screenshots leave blank; it shows in a browser.
