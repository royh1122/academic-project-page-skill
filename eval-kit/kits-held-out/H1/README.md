# Paperwren: A Gated Benchmark for Reading Synthetic Handwritten Forms Across Twelve Layout Families

> Synthetic test material. All people, institutions, venues, datasets and results are fictional. See FICTIONAL.md.

**Authors:** Mirela Exemplu*, Jürgen Beispiel*, Sofía Ejemplo, Taro Reidai, Noor Mithal, Pieter Voorbeeld, Inês Exemplo, Oskar Esimerkki†  
\* equal contribution, † corresponding author. Affiliations are in `team/authors.json`.  
**Status:** accepted at FDBT 2026 (Fictional Datasets and Benchmarks Track 2026); see `acceptance_email.txt`.  
**Current release:** v1.1 (2026-08-04). The paper describes v1.0.

## Abstract (from the paper, v1.0)

Paperwren is a benchmark for reading handwritten forms. It contains 12,400 synthetic forms in 12 layout families, each filled in by hand by one of 37 paid annotators and labelled field by field. The task is to return every field's value as text. We release the forms under a data-use agreement, a reference model, and a leaderboard on a held-out test split. The best model we tested reaches 84.6 field-level F1, and most errors come from crossed-out entries and dense tables.

## Access

See `access/ACCESS.md`. The data is shared on request under a data-use agreement.

## Limitations

- **English only.** Every form is in English; scores do not transfer to other languages or scripts.
- **Synthetic layouts.** The twelve layout families are designed, not collected; real forms are messier.
- **Small annotator pool.** 37 annotators from 3 countries wrote all forms, so handwriting styles are limited.

## What is in this folder

- `FICTIONAL.md` says that everything here is invented
- `LICENSE-FONTS.txt` GUST Font License for the Latin Modern fonts used in images and PDFs
- `LICENSE.md` licence of these generated test files
- `acceptance_email.txt` acceptance e-mail from FDBT 2026
- `access/` how to request access, and the draft data terms
- `citation/` BibTeX for the paper and for the dataset
- `code/` licence of the reference code
- `data/` sample forms and the maintainers' copy of the test labels
- `datasheet/` datasheet, split counts and per-family counts (v1.1)
- `figures/` figures for the page, with CAPTIONS.md
- `leaderboard/` leaderboard export
- `links.json` project, paper, code and access links
- `paper/` the paper (v1.0)
- `press/` a newsletter blurb from the communications office
- `release/` changelog
- `team/` authors and annotators

## Links

See `links.json`.

## Licences

- Code (`code/`): MIT, see `code/LICENSE`.
- Data: see `access/DATA_TERMS_DRAFT.md`.
- These generated test files as a whole: see LICENSE.md.
