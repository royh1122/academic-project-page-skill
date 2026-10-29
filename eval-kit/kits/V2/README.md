# Quillwave: Sparse-Sensor Reconstruction of Synthetic Ripple Fields

> Synthetic test material. All people, institutions, venues and results are fictional. See FICTIONAL.md.

**Authors:** Ada Placeholder  
**Affiliation:** Example University (fictional), Department of Imaginary Sciences  
**Status:** Research in preparation. No public code or preprint yet.

## Abstract

Quillwave reconstructs a full 256x256 ripple field from 64 point sensors. Ripple fields are procedurally generated sums of interfering circular waves: cheap to synthesise, but hard to interpolate, because the wave fronts between sensors are lost by smooth interpolation. Quillwave encodes the sensor readings into a 128-dimensional latent field code and decodes it with a coordinate-based field decoder. On RippleBench-Synthetic, a benchmark of 500 synthetic test fields generated for this work, Quillwave reaches 29.46 dB PSNR and 0.887 SSIM, 5.41 dB above radial-basis interpolation (the best baseline), which is a 71.2% lower mean squared error. It is also 1.36x faster than radial-basis interpolation at inference. All results are on synthetic fields only.

## Method

- Input: 64 point sensors on a regular 8x8 grid.
- A sensor encoder maps the readings to a 128-dimensional latent field code.
- A coordinate-based field decoder predicts the field value (and a confidence) at every pixel.
- Quillwave-Lite is the ablation without the latent code (decoder conditioned on raw readings).
- Trained on 2000 synthetic fields for 200 epochs (1.2M parameters).

## Main results

Reconstruction quality on RippleBench-Synthetic (64 sensors, 256x256 fields, mean over 5 training runs). Higher PSNR/SSIM is better; lower runtime is better.

| Method | PSNR (dB) | SSIM | Runtime (ms) |
|---|---:|---:|---:|
| Linear interpolation | 21.37 | 0.612 | **0.8** |
| Radial-basis interpolation | 24.05 | 0.701 | 6.4 |
| Quillwave-Lite (ablation) | 27.82 | 0.834 | 3.1 |
| Quillwave (ours) | **29.46** | **0.887** | 4.7 |

Quillwave improves PSNR by +5.41 dB over the best baseline (radial-basis interpolation), a 71.2% reduction in mean squared error, and runs 1.36x faster than it.

Sensor-count sweep (PSNR, dB) is in `results/sensor_sweep.csv`.

## Limitations

- **Baselines are not compute-matched.** Quillwave is trained for 3.5 GPU-hours, while the interpolation baselines need no training at all.
- **Synthetic fields only.** Every result is on RippleBench-Synthetic; no real sensor data was used, and behaviour on real measurements is unknown.
- **Confidence is not calibration.** The per-pixel confidence map that Quillwave outputs has not been checked against observed error rates, so it should not be read as a calibrated probability.

## What is in this folder

- `FICTIONAL.md` says that everything here is invented
- `README.md` this file
- `LICENSE.md` CC0 1.0 for all generated files
- `LICENSE-FONTS.txt` GUST Font License (Latin Modern)
- `citation.bib` BibTeX for this project
- `data/` user study data (personal data, see README_DATA.md)
- `figures/` figures and their captions
- `media/` tracking.gif: the dashboard's marker-tracking view, a marker ('buoy 1') following the reconstructed field over 4 s; field_demo_capture.mp4: a screen capture of the live dashboard
- `notes/` experiment log and meeting notes
- `results/` result tables (CSV/Markdown) and silent comparison loops
- `submission/` submission plan and author kit
- `summary.pdf` two-page project summary

## Links

No public code or preprint yet. A project summary is in `summary.pdf`.

## Licence

CC0 1.0 Universal for all generated files; Latin Modern fonts under the GUST Font License (LICENSE-FONTS.txt).
