# Run: Rscript -e 'testthat::test_file("materials/tests/test_or_chat.R")' (test_file runs in this folder)
source(file.path("..", "R", "or_chat.R"))

test_that("missing key stops clearly", {
  withr::with_envvar(c(OPENROUTER_API_KEY = ""),
    expect_error(or_chat("hi"), "OPENROUTER_API_KEY is not set"))
})

test_that("key falls back to a secret file (Nuvolos)", {
  f <- tempfile()
  writeLines("from-file\n", f)
  withr::with_envvar(c(OPENROUTER_API_KEY = ""),
    expect_equal(or_key(secret_file = f), "from-file"))
  withr::with_envvar(c(OPENROUTER_API_KEY = "from-env"),
    expect_equal(or_key(secret_file = f), "from-env"))
  withr::with_envvar(c(OPENROUTER_API_KEY = ""),
    expect_equal(or_key(secret_file = tempfile()), ""))
})

test_that("fenced JSON parses", {
  expect_equal(parse_json_reply("```json\n{\"label\": \"pos\"}\n```")$label, "pos")
})

test_that("prose around JSON parses", {
  expect_equal(parse_json_reply("Sure! {\"a\": 1} Hope this helps")$a, 1)
})

test_that("a JSON array parses", {
  expect_equal(parse_json_reply("[1, 2, 3]"), 1:3)
})

test_that("non-JSON returns NULL with warning", {
  expect_warning(r <- parse_json_reply("no json here"))
  expect_null(r)
})

test_that("HTTP error message is surfaced", {
  mock <- function(req) {
    httr2::response(status_code = 404,
      headers = list(`Content-Type` = "application/json"),
      body = charToRaw('{"error":{"message":"No endpoints found"}}'))
  }
  withr::with_envvar(c(OPENROUTER_API_KEY = "test"),
    httr2::with_mocked_responses(mock,
      expect_error(or_chat("hi", model = "x/y"), "404.*No endpoints found")))
})

test_that("successful reply returns the message content", {
  mock <- function(req) {
    httr2::response(status_code = 200,
      headers = list(`Content-Type` = "application/json"),
      body = charToRaw('{"choices":[{"message":{"role":"assistant","content":"OK"}}]}'))
  }
  withr::with_envvar(c(OPENROUTER_API_KEY = "test"),
    httr2::with_mocked_responses(mock,
      expect_equal(or_chat("hi", model = "x/y"), "OK")))
})
