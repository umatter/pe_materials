# Setup: Colab, Nuvolos, or your own machine

You need three things today: an **OpenRouter key**, **R**, and for Blocks 2 and 3 the coding agent
**pi**. How you get them depends on where you work:

| | Colab (Blocks 1, 2, 4) | Nuvolos RStudio (Blocks 2, 3) | Your own machine |
|---|---|---|---|
| R | ready | ready | install R + RStudio |
| Key | paste it into the key cell | provided by the course | set it yourself |
| pi | not used | installed | install it |

## The OpenRouter key

[OpenRouter](https://openrouter.ai) gives one key for many language models. In class you get a
course key. After the course, create your own: sign up, go to **Keys**, create a key, and set a
credit limit.

Treat a key like a password:

- never write it into a script, notebook, or anything you commit to git or upload;
- never paste it into a chat with a language model;
- if it leaks, revoke it on openrouter.ai and create a new one.

All course code reads the key from the environment variable `OPENROUTER_API_KEY`.

## Colab

Open a notebook from the links in the slides. Run the setup cells from the top. The key cell
asks for the key in a box, and clears its output so the key is not shown or saved with the
notebook. After a runtime restart, run the setup cells again.

The Gemini button in Colab is your coding assistant there: ask it to write or explain a cell.

## Nuvolos (RStudio)

Everything is installed, and the course files are in `/files/pee_2026` (one folder per block).
Open the RStudio app of the course space, then:

1. **R:** `source("R/or_chat.R")` (or the path given in the exercise) and call `or_chat("Hello")`.
   The key is read automatically.
2. **Terminal:** open a *new* terminal (Terminal tab → New Terminal) and check:

   ```bash
   pi --version
   [ -n "$OPENROUTER_API_KEY" ] && echo TRUE || echo FALSE
   ```

   If it prints `FALSE`: `export OPENROUTER_API_KEY="$(cat /secrets/OPENROUTER_API_KEY)"`.

   If `pi` is not found, install it into your home folder (the pi.dev installer does not work
   on Nuvolos, which has no Node.js; this downloads pi's ready-made program instead):

   ```bash
   mkdir -p ~/.local/opt ~/.local/bin
   curl -fsSL https://github.com/earendil-works/pi/releases/download/v1.4.0/pi-linux-x64.tar.gz | tar xz -C ~/.local/opt
   ln -sf ~/.local/opt/pi/pi ~/.local/bin/pi
   export PATH="$HOME/.local/bin:$PATH"
   pi --version
   ```

   The `export PATH=…` line holds for this terminal only: in a new terminal, run it again (or
   start pi as `~/.local/bin/pi`).
3. **Start pi** in your exercise folder:

   ```bash
   pi --model openrouter/anthropic/claude-haiku-5.5
   ```

## Your own machine

### R and RStudio

Install [R](https://cran.r-project.org) (4.3 or newer) and
[RStudio Desktop](https://posit.co/download/rstudio-desktop/), then in R:

```r
install.packages(c("httr2", "jsonlite", "dplyr", "readr", "tidyr", "ggplot2", "testthat"))
```

Download the helper `R/or_chat.R` from this repository (or clone the whole repository) and
`source()` it.

### The key for R

Put the key into your user `.Renviron` file, which R reads at start-up. In R:

```r
usethis::edit_r_environ()   # needs install.packages("usethis"); or open ~/.Renviron in any editor
```

Add the line `OPENROUTER_API_KEY=<your key>`, save, and restart R. Check with
`nzchar(Sys.getenv("OPENROUTER_API_KEY"))`, which should print `TRUE`. `.Renviron` lives in your
home folder, outside your projects, so it does not end up in git.

### pi

Install it (commands from [pi.dev](https://pi.dev); details in the
[Quickstart](https://pi.dev/docs/latest/quickstart)):

- **macOS / Linux:** `curl -fsSL https://pi.dev/install.sh | sh`. The installer needs Node.js
  22.19 or newer and offers to install it if it is missing; answer its questions with Enter for
  the default.
- **Windows (PowerShell):** `powershell -c "irm https://pi.dev/install.ps1 | iex"`. Also install
  [Git for Windows](https://git-scm.com/download/win): pi runs its shell commands in Git Bash
  (see [Run Pi on Windows](https://pi.dev/docs/latest/windows)).
- **With Node.js 22.19 or newer:** `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`

Open a new terminal and check with `pi --version`. Update later with `pi update` (installer) or
the npm command again.

Connect it to OpenRouter, in one of two ways:

- **Inside pi (easiest, also on Windows):** start `pi`, type `/login`, choose OpenRouter and paste
  your key. pi stores it in `~/.pi/agent/auth.json`; keep that file private. `/logout` removes it.
- **Environment variable:** pi also reads `OPENROUTER_API_KEY`.
  macOS / Linux: add `export OPENROUTER_API_KEY=<your key>` to `~/.zshrc` (macOS) or `~/.bashrc`
  (Linux). Windows: `setx OPENROUTER_API_KEY "<your key>"`. Then open a new terminal.

Start it in a project folder with the course model:

```bash
pi --model openrouter/anthropic/claude-haiku-5.5
```

Inside pi, `/model` switches models; Ctrl+S in that list saves one as your default.

### Before you let pi work on your own machine

pi does not ask before it edits files or runs commands: it acts with your user rights. On Nuvolos
that is contained to your course machine. On your laptop:

- use it only inside a project folder under git, and check what it changed with `git diff`;
- to keep it from running commands, start it with `--tools read,write,edit`;
- for full isolation, run it in a container (see pi's [Security](https://pi.dev/docs/latest/security) page).

## When something goes wrong

| Message | What to do |
|---|---|
| `OPENROUTER_API_KEY is not set` | Run the key cell (Colab), restart R after editing `.Renviron`, or open a new terminal |
| `HTTP 401` | The key is wrong or revoked: set it again |
| `HTTP 402` | The key's credit is used up |
| `HTTP 400: … is not a valid model ID` | Check the model name on [openrouter.ai/models](https://openrouter.ai/models) |
| `pi: command not found` | Open a new terminal after installing; on macOS/Linux check that the install folder is on your `PATH` |
| pi's `/model` list has no OpenRouter models | No key found: run `/login`, or start pi from a terminal where `OPENROUTER_API_KEY` is set |
| pi on Windows cannot find Bash | Install Git for Windows, then restart pi |
