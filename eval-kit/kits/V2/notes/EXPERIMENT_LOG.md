# Experiment log (Quillwave)

Internal working notes. Newest entries at the bottom.

## 2026-07-02, run 1
First end-to-end training on 2000 fields. Decoder diverged after a few epochs; learning-rate
schedule was wrong. No usable numbers.

## 2026-07-20, run 2
Fixed the schedule. Training is stable. Evaluation script still used the wrong sensor layout, so numbers
are not comparable to anything; discarded.

## 2026-08-14, run 3  (superseded by run 7)
Draft result with 64 sensors: PSNR 28.90 dB, SSIM 0.851.
Single training run, evaluated on a 100-field subset. These numbers went into the first draft of the
abstract.

## 2026-08-29, run 5
Added the confidence head. Quillwave-Lite ablation trained. Evaluation now uses the full
500-field test split.

## 2026-09-18, run 7
Final configuration: 200 epochs, 1.2M parameters, mean over
5 training runs on the full test split. These are the numbers in Table 1 and the
sensor sweep (`results/`). They supersede run 3.
