# Transcript: Quillwave explainer video

The video has no speech. These are its on-screen captions, also provided as `overview_explainer.en.vtt`. Synthetic test material. All people, institutions, venues and results are fictional.

[00:01] Quillwave is a fictional project, made as synthetic test material.

[00:06] The task: recover a full 256x256 ripple field from only 64 point sensors.

[00:10] Simple interpolation blurs the wave fronts between the sensors.

[00:14] Quillwave encodes the sensor readings into a compact latent field code.

[00:19] A field decoder then predicts a value and a confidence at every pixel.

[00:24] Left: linear interpolation of the sensors. Right: Quillwave.

[00:28] The wave fronts stay sharp as the sources move.

[00:32] On RippleBench-Synthetic, Quillwave reaches 29.46 dB PSNR.

[00:35] That is 5.41 dB above radial-basis interpolation.

[00:39] Limitations: all results are on synthetic fields only.

[00:42] The baselines are not compute-matched, and the confidence map is not calibrated.
