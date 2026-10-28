# LLM-powered R functions for text: structured annotation and map-reduce.
# Needs or_chat() and parse_json_reply() from ../R/or_chat.R (source it first).

# Ask a model to annotate a text and return the answer as an R list.
# schema_prompt describes the fields you want, one per line, e.g.
#   "policy_area: one of health, education, trade, other"
# Returns NULL with a warning when the reply contains no valid JSON.
annotate_text <- function(text, schema_prompt,
                          model = Sys.getenv("OPENROUTER_MODEL", "anthropic/claude-haiku-5.5")) {
  prompt <- paste0(
    "Annotate the text below. Return only a JSON object with these fields:\n",
    schema_prompt,
    "\n\nText:\n<<<\n", text, "\n>>>"
  )
  reply <- or_chat(prompt, model = model,
                   system = "You annotate documents for economic research. Answer with JSON only.")
  parse_json_reply(reply)
}

# Turn the fields of one annotation into a one-row data frame with one text
# column per field. Arrays become "a; b"; missing fields (or a failed
# annotation, NULL) become NA, so they show up when you count NAs.
fields_to_row <- function(fields, names) {
  values <- lapply(names, function(name) {
    x <- unlist(fields[[name]])
    if (length(x) == 0) NA_character_ else paste(x, collapse = "; ")
  })
  as.data.frame(setNames(values, names))
}

# Cut a text into pieces of at most chunk_chars characters.
chunk_text <- function(text, chunk_chars = 4000) {
  starts <- seq(1, nchar(text), by = chunk_chars)
  substring(text, starts, starts + chunk_chars - 1)
}

# Summarise a long text in two steps:
#   map:    one call per chunk, each in a fresh conversation;
#   reduce: one call that combines the chunk summaries.
# Makes ceiling(nchar(text) / chunk_chars) + 1 calls.
map_reduce_doc <- function(text, chunk_chars = 4000, map_prompt, reduce_prompt,
                           model = Sys.getenv("OPENROUTER_MODEL", "anthropic/claude-haiku-5.5")) {
  chunks <- chunk_text(text, chunk_chars)
  summaries <- vapply(chunks, function(chunk) {
    or_chat(paste0(map_prompt, "\n\n", chunk), model = model)
  }, character(1), USE.NAMES = FALSE)
  numbered <- paste0("Part ", seq_along(summaries), ":\n", summaries, collapse = "\n\n")
  or_chat(paste0(reduce_prompt, "\n\n", numbered), model = model)
}
