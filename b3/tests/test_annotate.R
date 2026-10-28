# Run from the project folder: testthat::test_file("tests/test_annotate.R")
# No API calls: or_chat() is replaced by a fake that records its prompts.
source(file.path("..", "..", "R", "or_chat.R"))
source(file.path("..", "R", "annotate.R"))

# Replace or_chat() for the duration of one test.
fake_or_chat <- function(reply) {
  calls <- new.env()
  calls$prompts <- character(0)
  testthat::local_mocked_bindings(
    or_chat = function(prompt, ...) {
      calls$prompts <- c(calls$prompts, prompt)
      if (is.function(reply)) reply(prompt) else reply
    },
    .package = "base", .env = parent.frame()
  )
  calls
}

test_that("annotate_text reads a fenced JSON reply", {
  fake_or_chat("```json\n{\"label\": \"health\"}\n```")
  out <- annotate_text("A bill about hospitals.", "label: the policy area")
  expect_equal(out, list(label = "health"))
})

test_that("annotate_text puts the schema and the text into the prompt", {
  calls <- fake_or_chat("{\"label\": \"health\"}")
  annotate_text("A bill about hospitals.", "label: the policy area")
  expect_match(calls$prompts, "label: the policy area", fixed = TRUE)
  expect_match(calls$prompts, "A bill about hospitals.", fixed = TRUE)
})

test_that("annotate_text returns NULL with a warning on prose", {
  fake_or_chat("I think this bill is about health.")
  expect_warning(out <- annotate_text("A bill.", "label: the policy area"))
  expect_null(out)
})

test_that("map_reduce_doc makes one call per chunk plus one", {
  calls <- fake_or_chat("a summary")
  text <- strrep("x", 10001)
  out <- map_reduce_doc(text, chunk_chars = 4000,
                        map_prompt = "Summarise this part:",
                        reduce_prompt = "Combine these summaries:")
  expect_length(calls$prompts, ceiling(nchar(text) / 4000) + 1)
  expect_equal(out, "a summary")
})

test_that("the reduce step sees the chunk summaries, not the text", {
  calls <- fake_or_chat(function(prompt) {
    if (grepl("^Summarise", prompt)) paste("summary of", nchar(prompt)) else "final"
  })
  map_reduce_doc(strrep("y", 5000), chunk_chars = 4000,
                 map_prompt = "Summarise this part:",
                 reduce_prompt = "Combine these summaries:")
  reduce <- calls$prompts[3]
  expect_match(reduce, "^Combine these summaries:")
  expect_match(reduce, "summary of")
  expect_false(grepl("yyyy", reduce))
})

test_that("chunk_text cuts a text into pieces of chunk_chars characters", {
  chunks <- chunk_text("abcdefghij", 4)
  expect_equal(chunks, c("abcd", "efgh", "ij"))
  expect_equal(paste(chunks, collapse = ""), "abcdefghij")
})

test_that("fields_to_row gives one row, whatever shape the fields have", {
  fields <- list(short_title = c("Making Opportunities for Mothers Act", "MOM Act"),
                 agencies = c("HHS", "Treasury"), creates_spending = TRUE)
  row <- fields_to_row(fields, c("short_title", "policy_area", "agencies", "creates_spending"))
  expect_equal(nrow(row), 1)
  expect_equal(row$short_title, "Making Opportunities for Mothers Act; MOM Act")
  expect_equal(row$agencies, "HHS; Treasury")
  expect_true(is.na(row$policy_area))
  expect_equal(row$creates_spending, "TRUE")
})

test_that("fields_to_row turns a failed annotation (NULL) into NAs", {
  row <- fields_to_row(NULL, c("short_title", "agencies"))
  expect_equal(nrow(row), 1)
  expect_true(all(is.na(row)))
})
