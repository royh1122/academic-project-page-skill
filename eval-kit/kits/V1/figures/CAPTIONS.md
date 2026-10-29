# Figure captions

## figures/overview.png

Quillwave pipeline. From left to right: the 64 point sensors, the sensor encoder, the 128-dimensional latent field code, the field decoder, and the reconstructed 256x256 field.

## figures/results_panels.png

Results on RippleBench-Synthetic. Top row: (a) PSNR and (b) SSIM against the number of sensors (16, 32, 64, 128), and (c) runtime per field. Bottom row: (d) histogram of absolute per-pixel error, (e) per-scene PSNR of Quillwave against radial-basis interpolation (points above the diagonal favour Quillwave), and (f) validation PSNR during training. As the left panels show, the gap grows with fewer sensors.

## figures/qualitative_grid.jpg

Qualitative comparison on four test scenes. Columns, left to right: sensor map, linear interpolation, radial-basis interpolation, Quillwave (ours), ground truth. Note how the wave fronts in the fourth column stay sharp.

## figures/qualitative/scene_01.jpg ... scene_04.jpg

One test scene each: sensor input on the left, Quillwave in the middle, ground truth on the right.
