# Helpers for calling an LLM through OpenRouter from R.
# Needs the packages httr2 and jsonlite, and your key in the environment
# variable OPENROUTER_API_KEY.

# Install only the packages that are missing (safe to run twice).
ensure_packages <- function(pkgs) {
  missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing) > 0) install.packages(missing)
  invisible(NULL)
}

# The OpenRouter key: from the environment, else from the Nuvolos space
# secret file (RStudio sessions on Nuvolos do not inherit the variable).
or_key <- function(secret_file = "/secrets/OPENROUTER_API_KEY") {
  key <- Sys.getenv("OPENROUTER_API_KEY")
  if (!nzchar(key) && file.exists(secret_file)) {
    key <- trimws(paste(readLines(secret_file, warn = FALSE), collapse = ""))
  }
  key
}

# Send one prompt to a model and return the reply as a character string.
or_chat <- function(prompt,
                    model = Sys.getenv("OPENROUTER_MODEL", "anthropic/claude-haiku-5.5"),
                    system = NULL,
                    temperature = 0,
                    max_retries = 3) {
  key <- or_key()
  if (!nzchar(key)) {
    stop("OPENROUTER_API_KEY is not set. Run the key cell first.", call. = FALSE)
  }

  messages <- list(list(role = "user", content = prompt))
  if (!is.null(system)) {
    messages <- c(list(list(role = "system", content = system)), messages)
  }

  resp <- httr2::request("https://openrouter.ai/api/v1/chat/completions") |>
    httr2::req_auth_bearer_token(key) |>
    httr2::req_body_json(list(model = model,
                              messages = messages,
                              temperature = temperature)) |>
    httr2::req_retry(max_tries = max_retries,
                     is_transient = \(r) httr2::resp_status(r) %in% c(429, 500, 502, 503)) |>
    httr2::req_error(body = \(r) {
      msg <- tryCatch(httr2::resp_body_json(r)$error$message,
                      error = \(e) NULL)
      paste0("HTTP ", httr2::resp_status(r), ": ",
             if (is.null(msg)) "no error message from OpenRouter" else msg)
    }) |>
    httr2::req_perform()

  httr2::resp_body_json(resp)$choices[[1]]$message$content
}

# Turn a model reply into an R object if it contains JSON.
# Strips ```json fences and surrounding prose; returns NULL with a warning
# when no JSON can be read.
parse_json_reply <- function(text) {
  text <- gsub("```(json)?", "", text)
  start <- regexpr("[\\[{]", text)
  if (start < 0) {
    warning("No JSON found in the reply.", call. = FALSE)
    return(NULL)
  }
  open <- substr(text, start, start)
  close <- if (open == "{") "}" else "]"
  ends <- gregexpr(close, text, fixed = TRUE)[[1]]
  candidate <- substr(text, start, max(ends))
  tryCatch(jsonlite::fromJSON(candidate),
           error = \(e) {
             warning("The reply contains text that is not valid JSON.", call. = FALSE)
             NULL
           })
}
