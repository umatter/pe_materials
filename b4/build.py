"""Build 04_can_you_trust_it.ipynb. Run: python3 materials/b4/build.py"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from nbtools import code, md, standard_cells, write_notebook  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
DATA_URL = "https://raw.githubusercontent.com/umatter/pe_materials/main/b4/data/imdb_sample.csv"

cells = [
    md("""# Block 4: Can you trust it?

This notebook runs in Colab's **R** runtime (Runtime → Change runtime type → R).

You let three models label 100 movie reviews as positive or negative, with two prompts, and
compare their labels with the human ones. That is the core of the technical appendix your group
writes for its project: **does the prompt work, with which model, and how do you know?**

Two kinds of AI appear in this notebook:
- **The models you call from R** through the OpenRouter API (`or_chat()`): they do the labelling.
- **Gemini in Colab**, which helps you write and fix the code: your coding assistant.

A full run makes about 620 API calls, takes about three minutes and costs about 3 US cents."""),
    *standard_cells(["ggplot2"]),

    md("""## 1. The data: 100 reviews with a human label

Each review comes with a gold label from the reviewer's own star rating (positive or negative),
50 of each. Source and licence: `data/README.md`."""),
    code(f"""data_file <- "data/imdb_sample.csv"
if (!file.exists(data_file)) data_file <- "{DATA_URL}"
reviews <- read.csv(data_file)
table(reviews$label)
cat(strwrap(reviews$text[1], 90), sep = "\\n")"""),

    md("""## 2. Agreement: accuracy and Cohen's kappa

Accuracy is the share of items where two label vectors agree. Cohen's kappa corrects for the
agreement you would get by chance: 1 is perfect agreement, 0 is chance level."""),
    code("""cohen_kappa <- function(a, b) {
  ok <- !is.na(a) & !is.na(b)
  a <- a[ok]; b <- b[ok]
  levels <- union(a, b)
  a <- factor(a, levels); b <- factor(b, levels)
  p_observed <- mean(a == b)
  p_chance <- sum(prop.table(table(a)) * prop.table(table(b)))
  if (p_chance == 1) return(if (p_observed == 1) 1 else NA_real_)
  (p_observed - p_chance) / (1 - p_chance)
}"""),
    md("### Self-check"),
    code("""stopifnot(
  "Identical labels should give kappa 1" = cohen_kappa(c(1, 1, 0, 0), c(1, 1, 0, 0)) == 1,
  "Chance-level labels should give kappa 0" = cohen_kappa(c(1, 1, 0, 0), c(1, 0, 1, 0)) == 0
)
cat("Self-check passed.")"""),

    md("""## 3. Two prompts

- **Prompt A (zero-shot):** the bare question, one word back.
- **Prompt B (codebook):** a definition of the classes, rules for hard cases, two examples, and
  JSON output.

Both functions return `"positive"`, `"negative"`, or `NA` when the call fails or the reply cannot be read."""),
    code("""prompt_a <- function(text) {
  paste0("Is the sentiment of this movie review positive or negative? ",
         "Answer with one word.\\n\\nReview: ", text)
}

codebook <- 'You label the sentiment of movie reviews for a research project.

Codebook:
- positive: the reviewer recommends the film or rates it well overall.
- negative: the reviewer advises against the film or rates it poorly overall.
Rules:
- Judge the reviewer\\'s overall verdict on the film, not the mood of the story it describes.
- If the review is mixed, choose the side of the final verdict.

Examples:
Review: "The plot is grim and everyone dies, but it is the best war film I have seen."
{"label": "positive"}
Review: "Great cast, lovely music, and still two hours I will never get back."
{"label": "negative"}

Reply with JSON only: {"label": "positive"} or {"label": "negative"}.'

prompt_b <- function(text) paste0("Review: ", text)

# Read a reply into a label: one word for prompt A, JSON for prompt B
read_label <- function(reply, json = FALSE) {
  if (json) reply <- suppressWarnings(parse_json_reply(reply))$label
  if (is.null(reply) || length(reply) != 1) return(NA_character_)
  reply <- tolower(reply)
  is_pos <- grepl("positive", reply); is_neg <- grepl("negative", reply)
  if (is_pos && !is_neg) "positive" else if (is_neg && !is_pos) "negative" else NA_character_
}"""),
    md("""Labelling 100 reviews one by one takes a while, so `label_all()` sends several requests at
the same time (`mc.cores`). A failed call becomes `NA` (a missing label) instead of stopping the loop;
the progress line says why labels are missing, and a run where every call fails stops with the error.
An empty reply is asked once more before it counts as missing."""),
    code("""cores <- 8  # parallel requests; set to 1 if the cell hangs

label_all <- function(texts, model, prompt = c("A", "B"), temperature = 0) {
  prompt <- match.arg(prompt)
  # One review: a label, or NA and the reason
  one <- function(text) tryCatch({
    ask <- function() if (prompt == "A") or_chat(prompt_a(text), model = model, temperature = temperature)
                      else or_chat(prompt_b(text), model = model, system = codebook, temperature = temperature)
    reply <- ask()
    if (!is.character(reply)) reply <- ask()  # an empty reply happens under load: ask once more
    if (!is.character(reply) || length(reply) != 1) {
      list(label = NA_character_, why = "reply without text")
    } else {
      label <- read_label(reply, json = prompt == "B")
      list(label = label, why = if (is.na(label)) "reply not in the codebook" else NA_character_)
    }
  }, error = function(e) list(label = NA_character_, why = conditionMessage(e)))

  start <- Sys.time()
  out <- parallel::mclapply(texts, one, mc.cores = cores, mc.preschedule = FALSE)
  ok <- vapply(out, is.list, logical(1))  # a crashed parallel job returns an error object
  labels <- ifelse(ok, vapply(out, function(x) if (is.list(x)) x$label else NA_character_, ""), NA_character_)
  why <- ifelse(ok, vapply(out, function(x) if (is.list(x)) x$why else NA_character_, ""), "parallel job failed")
  cat(sprintf("%-32s prompt %s: %3d labels, %2d missing, %4.0f s\\n", model, prompt,
              length(labels), sum(is.na(labels)),
              as.numeric(difftime(Sys.time(), start, units = "secs"))))
  if (all(is.na(labels))) stop("No labels from ", model, ": ", why[!is.na(why)][1], call. = FALSE)
  if (any(is.na(labels))) cat("  missing because:", paste(unique(why[!is.na(why)]), collapse = "; "), "\\n")
  labels
}

# Try it on three reviews before the full run
label_all(reviews$text[1:3], "anthropic/claude-haiku-5.5", "B")"""),

    md("""## 4. Label everything: 3 models × 2 prompts

- `anthropic/claude-haiku-5.5`: small, cheap, closed model
- `deepseek/deepseek-v4.1-flash`: open weights
- `meta-llama/llama-4-scout`: older and smaller, the one most likely to disagree

600 calls. Watch the progress lines."""),
    code("""models <- c("anthropic/claude-haiku-5.5", "deepseek/deepseek-v4.1-flash",
            "meta-llama/llama-4-scout")
runs <- expand.grid(model = models, prompt = c("A", "B"), stringsAsFactors = FALSE)

labels <- list()
for (i in seq_len(nrow(runs))) {
  key <- paste(runs$model[i], runs$prompt[i])
  labels[[key]] <- label_all(reviews$text, runs$model[i], runs$prompt[i])
}"""),

    md("""## 5. How well does each run agree with the human labels?

`accuracy` and `kappa` use only the reviews a run labelled; `correct` is the share of all 100
reviews it labelled correctly, so a missing label counts as wrong. A run that skips the hard
reviews can look best on `kappa`: always read `missing` next to it."""),
    code("""results <- data.frame(
  model = runs$model,
  prompt = runs$prompt,
  missing = sapply(labels, function(x) sum(is.na(x))),
  accuracy = sapply(labels, function(x) round(mean(x == reviews$label, na.rm = TRUE), 3)),
  kappa = sapply(labels, function(x) round(cohen_kappa(x, reviews$label), 3)),
  correct = sapply(labels, function(x) round(mean(!is.na(x) & x == reviews$label), 3)),
  row.names = NULL
)
results[order(-results$correct), ]"""),
    code("""library(ggplot2)
ggplot(results, aes(x = kappa, y = model, fill = prompt)) +
  geom_col(position = "dodge") +
  scale_fill_manual(values = c(A = "#A2AEB9", B = "#3C3C3C")) +
  labs(x = "Cohen's kappa with the human labels", y = NULL,
       fill = "Prompt", title = "Agreement with the gold standard") +
  theme_minimal()"""),

    md("""## 6. Do the models agree with each other?

High agreement between models is not the same as being right: two models can share the same
mistakes. Kappa between every pair of models (prompt B):"""),
    code("""b_labels <- labels[paste(models, "B")]
names(b_labels) <- sub("/.*", "", models)
pairs <- outer(names(b_labels), names(b_labels),
               Vectorize(function(m1, m2) round(cohen_kappa(b_labels[[m1]], b_labels[[m2]]), 2)))
dimnames(pairs) <- list(names(b_labels), names(b_labels))
pairs"""),

    md("""## 7. Read the disagreements

Numbers tell you how often the model is wrong, not why. Read the items where the best run
disagrees with the human label. Is the model wrong, or the gold label?"""),
    code("""best <- paste(results$model, results$prompt)[which.max(results$correct)]
wrong <- which(labels[[best]] != reviews$label | is.na(labels[[best]]))
cat("Best run:", best, "-", length(wrong), "disagreements\\n\\n")
for (i in head(wrong, 5)) {
  cat(sprintf("[%s] human: %s, model: %s\\n", reviews$id[i], reviews$label[i], labels[[best]][i]))
  cat(strwrap(substr(reviews$text[i], 1, 400), 90), sep = "\\n")
  cat("\\n")
}"""),

    md("""## 8. Same prompt, same model, same answer?

At temperature 0 most models answer (almost) the same way every time; at higher temperatures
they need not. Label the first 20 reviews again with Llama at temperature 1 and compare with
its temperature-0 labels."""),
    code("""rerun <- label_all(reviews$text[1:20], "meta-llama/llama-4-scout", "B", temperature = 1)
first <- labels[["meta-llama/llama-4-scout B"]][1:20]
both <- !is.na(rerun) & !is.na(first)
cat("Same label in", sum(rerun[both] == first[both]), "of", sum(both),
    "reviews labelled in both runs;", sum(!both), "missing in one of the runs\\n")"""),

    md("""## 9. This is your technical appendix

Your project's technical appendix (30% of the grade) asks how your prompt performs under
different settings and models. This notebook is a template for it:

1. **Gold standard:** human labels for a sample of your items (here: 100 reviews).
2. **Prompt variants:** at least two, stated in full (here: A and B).
3. **Models:** at least two, with exact names and the date of the run.
4. **Agreement:** accuracy and kappa with the gold labels, plus how many labels are missing.
5. **Disagreements:** read them and say what goes wrong.
6. **Stability:** does a rerun give the same labels?

The next cell writes the results table to a file you can download (folder icon on the left)."""),
    code("""results$date <- format(Sys.Date())
write.csv(results, "appendix_results.csv", row.names = FALSE)
results"""),
    md("### Self-check"),
    code("""stopifnot(
  "Expected 6 runs (3 models x 2 prompts)" = nrow(results) == 6,
  "Some kappa values are missing" = all(!is.na(results$kappa)),
  "The results file was not written" = file.exists("appendix_results.csv")
)
cat("Self-check passed.")"""),

    md("""## Your turn

Pick one, and ask Gemini to help with the code:

- Change prompt B: add a third label `mixed` to the codebook. What happens to accuracy, and how
  would you compare a three-class model with two-class human labels?
- Add a fourth model from [openrouter.ai/models](https://openrouter.ai/models) and rerun
  sections 4–6.
- Take 20 items from your own project's data, label them yourself, and run prompt B on them."""),
]

write_notebook(cells, HERE / "04_can_you_trust_it.ipynb")
