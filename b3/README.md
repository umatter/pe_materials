# Block 3: LLMs inside the pipeline

An RStudio project: US congressional bills in, one table row per bill out, with a language model
doing the reading inside ordinary R functions.

- Exercise: [`TASK_pi.md`](TASK_pi.md)
- Setup (key, R, pi): [`../SETUP.md`](../SETUP.md)
- Needs the shared helper `../R/or_chat.R`; keep this folder next to `R/` as in the repository.

| File | What it does |
|---|---|
| `R/annotate.R` | `annotate_text()` (fields as JSON), `chunk_text()`, `map_reduce_doc()` |
| `R/pipeline.R` | runs both on every bill in `data/`, writes `output/summary.csv` |
| `tests/test_annotate.R` | tests without API calls: `testthat::test_file("tests/test_annotate.R")` |
| `data/` | two bills of the US House of Representatives (public domain, from govinfo.gov) |

A full run (two bills) makes 11 API calls (8 for the long bill, 3 for the short one) and takes about half a minute.
