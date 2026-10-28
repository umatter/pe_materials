# Block 3: extend an LLM pipeline with pi

The project in this folder turns US congressional bills into a table, with one row per bill:

- `R/annotate.R`: two LLM-powered R functions.
  - `annotate_text()` asks a model for fixed fields and gets them back as JSON (structured output).
  - `map_reduce_doc()` summarises a long text chunk by chunk (map), then combines the chunk
    summaries (reduce).
- `R/pipeline.R`: reads every bill in `data/`, runs both functions, and writes `output/summary.csv`.
- `tests/test_annotate.R`: tests that run without the API (a fake `or_chat()` replaces the real one).

Setup (key, R, pi): see [`../SETUP.md`](../SETUP.md).

## 0. Run it yourself first (10 min)

1. Open `pipeline.Rproj` in RStudio.
2. In the R console, run the tests, then the pipeline:

   ```r
   if (!requireNamespace("testthat", quietly = TRUE)) install.packages("testthat")
   testthat::test_file("tests/test_annotate.R")
   source("R/pipeline.R")
   read.csv("output/summary.csv")
   ```

3. Check two facts in `output/summary.csv` against the bill texts in `data/`, for example a deadline
   or an agency. Does the MOM Act summary say anything odd?

## 1. Work with pi (25 min)

Open a **new terminal** in RStudio (Terminal → New Terminal), go to this folder, put it under git,
and start pi:

```bash
cd /files/pee_2026/b3         # own laptop: cd pe_materials/b3
git config --global user.name >/dev/null || git config --global user.name "Student"
git config --global user.email >/dev/null || git config --global user.email "student@example.com"
git init -q && git add -A && git commit -qm "start"
pi --model openrouter/anthropic/claude-haiku-5.5
```

Give pi the tasks below **one at a time**. After each one: read what it changed with `git diff`,
run the tests and the pipeline yourself, and commit (`git add -A && git commit -m "task a"`) only
if you agree with the change. To undo a change you do not want: `git checkout -- . && git clean -fd`
(this also deletes new files pi created).

**a) Add a field.** Paste into pi:

> In R/pipeline.R, add a field `beneficiaries` to the schema: who the bill is meant to help, in a
> few words. Add it as a column of output/summary.csv. Do not change R/annotate.R.

Run `source("R/pipeline.R")` and look at the new column. Is the field well defined?

**b) Fix the one-chunk summary.** The MOM Act fits into one chunk, but the reduce step still runs
and the model writes "only Part 1 was provided". Paste into pi:

> In R/annotate.R, change map_reduce_doc() so that a text that fits into one chunk is summarised
> with a single call: no reduce step. Update tests/test_annotate.R to match, and add a test for the
> one-chunk case. Then tell me how to run the tests.

Run the tests. Did pi change a test only to make it pass? Read the test diff line by line.

**c) Better chunks.** `chunk_text()` cuts the text every 4000 characters, often in the middle of a
word. Paste into pi:

> Change chunk_text() in R/annotate.R so that chunks end at a line break, not in the middle of a
> word, and stay at most chunk_chars long. Add a test that no chunk ends in the middle of a word.

## 2. Debrief (5 min)

- Which of pi's changes did you keep as they were? Which did you fix or throw away, and why?
- `creates_spending` is `TRUE` for the MOM Act, yet the bill does not say how much money it
  authorises. Is that the model's mistake, or the definition in the schema?
- Your project: which column of a table like this would you need? What would you check by hand
  before you trust it? (That is Block 4.)

## Safety

pi does not ask before it edits files or runs commands. Work inside a git repository, read every
diff, and on your own laptop see "Before you let pi work on your own machine" in
[`../SETUP.md`](../SETUP.md).
