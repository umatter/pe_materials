# The Block 3 pipeline: bill texts in, one row per bill out.
# Run from the project folder: Rscript R/pipeline.R  (or source() it in RStudio)

source(file.path("..", "R", "or_chat.R"))
source(file.path("R", "annotate.R"))
ensure_packages(c("httr2", "jsonlite"))

model <- Sys.getenv("OPENROUTER_MODEL", "anthropic/claude-haiku-5.5")

# 1. The fields we want for every bill (structured output)
schema <- paste(
  "short_title: the bill's short title as written in the text",
  "policy_area: one of health, education, social_welfare, trade, foreign_policy, other",
  "agencies: the federal agencies the bill gives tasks to, as an array of names",
  "creates_spending: true if the bill authorises or appropriates money, else false",
  sep = "\n"
)

# 2. Prompts for the long-document summary (map-reduce)
map_prompt <- paste("Summarise this part of a US congressional bill in 2-3 sentences.",
                    "Keep numbers, deadlines and agency names exactly as written.")
reduce_prompt <- paste("These are summaries of consecutive parts of one US congressional bill.",
                       "Write one summary of the whole bill in at most 4 sentences.")

# 3. Run both steps on every bill
fields <- c("short_title", "policy_area", "agencies", "creates_spending")
files <- list.files("data", pattern = "\\.txt$", full.names = TRUE)
rows <- lapply(files, function(f) {
  text <- paste(readLines(f, warn = FALSE), collapse = "\n")
  message("Annotating ", basename(f), " (", nchar(text), " characters)")
  annotation <- annotate_text(text, schema, model = model)   # NULL if the reply had no JSON
  cbind(
    data.frame(file = basename(f), n_chars = nchar(text)),
    fields_to_row(annotation, fields),
    summary = map_reduce_doc(text, chunk_chars = 4000, map_prompt, reduce_prompt, model = model)
  )
})
summary_table <- do.call(rbind, rows)

# 4. Save the table
dir.create("output", showWarnings = FALSE)
write.csv(summary_table, file.path("output", "summary.csv"), row.names = FALSE)
message("Wrote output/summary.csv (", nrow(summary_table), " rows, model ", model, ")")
