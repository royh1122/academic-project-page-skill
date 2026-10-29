# Table 1

Reconstruction quality on RippleBench-Synthetic (64 sensors, 256x256 fields, mean over 5 training runs). Higher PSNR/SSIM is better; lower runtime is better.

| Method | PSNR (dB) | SSIM | Runtime (ms) |
|---|---:|---:|---:|
| Linear interpolation | 21.37 | 0.612 | **0.8** |
| Radial-basis interpolation | 24.05 | 0.701 | 6.4 |
| Quillwave-Lite (ablation) | 27.82 | 0.834 | 3.1 |
| Quillwave (ours) | **29.46** | **0.887** | 4.7 |

Quillwave improves PSNR by +5.41 dB over the best baseline (radial-basis interpolation), a 71.2% reduction in mean squared error, and runs 1.36x faster than it.
