"""Build 01_first_call.ipynb. Run: python3 materials/b1/build.py"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from nbtools import code, md, standard_cells, write_notebook  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent

cells = [
    md("""# Block 1: Your first API call from R

This notebook runs in Colab's **R** runtime (Runtime → Change runtime type → R).

Two kinds of AI appear in this notebook:
- **The model you call from R** through the OpenRouter API (`or_chat()`): part of your analysis.
- **Gemini in Colab**, which helps you write and fix the code: your coding assistant.

Setup help (key, errors): `SETUP.md` in the course repository."""),
    *standard_cells(),
    md("## 1. Your first call"),
    code('reply <- or_chat("In one sentence: why might an economist call an LLM from R instead of using a chat window?")\ncat(reply)'),
    md("### Self-check"),
    code('stopifnot("The call returned no text. Is your key set?" = is.character(reply) && nchar(reply) > 0)\ncat("Self-check passed.")'),
    md("""## 2. What `or_chat()` sends

`or_chat()` is a short function: it sends one HTTP request to OpenRouter and returns the text of
the reply. Here is the same request written out, so you can see everything that goes over the
wire and everything that comes back."""),
    code("""resp <- httr2::request("https://openrouter.ai/api/v1/chat/completions") |>
  httr2::req_auth_bearer_token(or_key()) |>
  httr2::req_body_json(list(
    model = "anthropic/claude-haiku-5.5",
    messages = list(list(role = "user", content = "Name one use of GDP data. Five words at most.")),
    temperature = 0
  )) |>
  httr2::req_perform()

body <- httr2::resp_body_json(resp)
cat(body$choices[[1]]$message$content, "\\n")
str(body$usage)   # tokens in and out: what you pay for"""),
    md("""The reply is JSON: the text sits in `choices[[1]]$message$content`; `usage` counts the
tokens. Everything else in your analysis is ordinary R."""),
    md("""## 3. Roles: system and user

You saw system, user and assistant messages yesterday. In `or_chat()` the system message is an
argument. Same question, two system messages:"""),
    code("""q <- "Is a minimum wage increase good for workers?"
cat(or_chat(q, system = "You are a labour economist. Answer in two sentences, citing the main trade-off."), "\\n\\n")
cat(or_chat(q, system = "Answer only 'yes', 'no' or 'it depends'."))"""),
    md("""## 4. Another model, same code

OpenRouter serves many models behind one API. Only the `model` argument changes."""),
    code("""q <- "In one sentence: what does the Phillips curve describe?"
for (m in c("anthropic/claude-haiku-5.5", "deepseek/deepseek-v4.1-flash")) {
  cat(m, ":\\n", or_chat(q, model = m), "\\n\\n", sep = "")
}"""),
    md("""## 5. Temperature

At `temperature = 0` the model (almost always) picks its most likely answer. At higher values the
answers can vary. Run the cell twice: which answers change?"""),
    code("""for (t in c(0, 1)) {
  answers <- vapply(1:3, \\(i) or_chat("Invent a name for a podcast about Swiss economics. Reply with the name only.", temperature = t), character(1))
  cat("temperature", t, ":", answers, "\\n")
}"""),
    md("""## 6. A reply you can compute with

For analysis you want data, not prose. Ask for JSON and turn it into an R object with
`parse_json_reply()`."""),
    code("""reply <- or_chat(paste(
  "Classify the sentiment of each headline as positive, negative or neutral.",
  "Reply only with a JSON array of objects with the keys id and sentiment.",
  "1: Swiss exports hit record high",
  "2: Unemployment rises for third month",
  "3: Central bank leaves rates unchanged",
  sep = "\\n"))
labels <- parse_json_reply(reply)
labels"""),
    md("### Self-check"),
    code("""stopifnot("parse_json_reply() returned no table: look at `reply`" = is.data.frame(labels),
          "expected three rows, one per headline" = nrow(labels) == 3,
          "expected a column `sentiment`" = "sentiment" %in% names(labels))
cat("Self-check passed.")"""),
    md("""## 7. Your turn, with Gemini

Now let Gemini write the code. Click **generate** in the empty cell below and ask, for example:

> Write R code that calls the function `or_chat(prompt)` once for each of the three questions in
> the character vector `questions` and stores the questions and answers in a data frame called
> `answers` with the columns `question` and `answer`.

Read the code before you run it. Does it call `or_chat()` once per question?"""),
    code("""questions <- c("What is inflation? One sentence.",
               "What is a recession? One sentence.",
               "What is GDP? One sentence.")"""),
    code(""),
    md("### Self-check"),
    code("""stopifnot("Create the data frame `answers` first" = exists("answers") && is.data.frame(answers),
          "answers should have one row per question" = nrow(answers) == length(questions),
          "answers needs the columns question and answer" = all(c("question", "answer") %in% names(answers)))
cat("Self-check passed.")"""),
    md("""## What this means for your project

Every model call in your project can be an R function call like these: you can repeat it, vary
the prompt, the model and the temperature, and keep the results in a table. That is what the
technical appendix of your project asks you to do."""),
]

write_notebook(cells, HERE / "01_first_call.ipynb")
