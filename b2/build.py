"""Build 02_data_handling_colab.ipynb. Run: python3 materials/b2/build.py"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from nbtools import code, md, standard_cells, write_notebook  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
TASK = (HERE / "pi" / "TASK.md").read_text().strip()
# The Colab notebook makes no API calls: it needs the package cell, not the key and helper cells.
setup = [md("## Setup\nRun the next cell once: it installs the packages that are missing. "
            "Run it again after a runtime restart. Problems with the setup: see "
            "[SETUP.md](https://github.com/umatter/pe_materials/blob/main/SETUP.md)."),
         standard_cells(["readr", "dplyr", "tidyr"])[1]]

FINAL_CHECK = """expected_cols <- c("iso3", "country", "region", "income_group", "year", "gdp_bn",
                   "population", "gdp_pc", "unemployment", "inflation")
num_cols <- expected_cols[5:10]
stopifnot("Create the data frame `clean` first" = exists("clean") && is.data.frame(clean))
che <- clean[clean$iso3 == "CHE" & clean$year == 2020, ]
stopifnot(
  "clean should have 260 rows: 26 countries x 10 years" = nrow(clean) == 260,
  "columns should be exactly the ones in the task, in that order" =
    identical(names(clean), expected_cols),
  "year to inflation should all be numeric" =
    all(vapply(as.data.frame(clean)[num_cols], is.numeric, logical(1))),
  "aggregates (World, EU, euro area, Sub-Saharan Africa) should be gone" =
    !any(clean$iso3 %in% c("WLD", "EUU", "EMU", "SSF")),
  "no '..' should be left anywhere" = !any(as.matrix(clean) == "..", na.rm = TRUE),
  "region names should have no spaces at the ends" = all(clean$region == trimws(clean$region)),
  "inflation should have 11 missing values (Argentina, Venezuela)" = sum(is.na(clean$inflation)) == 11,
  "gdp_bn should have 9 missing values (South Sudan)" = sum(is.na(clean$gdp_bn)) == 9,
  "Switzerland 2020: gdp_bn about 756, gdp_pc about 87,500" =
    abs(che$gdp_bn - 756) < 1 && abs(che$gdp_pc - 87530) < 10,
  "rows should be sorted by iso3 and year" =
    !is.unsorted(paste(clean$iso3, clean$year)),
  "wdi_clean.csv should exist" = file.exists("wdi_clean.csv"))
cat("All self-checks passed.")"""


def step(title, text, prompt, name):
    return [
        md(f"""## {title}

{text}

**Ask Gemini** (click *generate* in the empty cell below, or open the Gemini panel), for example:

> {prompt}

Read the code before you run it. Call the result `{name}`."""),
        code(""),
    ]


cells = [
    md("""# Block 2: AI-assisted data handling (Colab + Gemini)

This notebook runs in Colab's **R** runtime (Runtime → Change runtime type → R).

**To keep your work, click *Copy to Drive* in the toolbar first.** Opened from the course link, the
notebook is not saved: your changes and outputs are lost when you close the tab. The copy goes to
*Colab Notebooks* in your Google Drive.

Today the AI is **Gemini in Colab**, your coding assistant: it suggests code, you decide what runs.
This notebook makes no calls to a language model from R, so you need no key.

After the break you give the *same task* to **pi**, a coding agent in RStudio, and compare.

How to use Gemini here:
- In an empty code cell, click **generate** and describe what the cell should do.
- When a cell fails, click **Explain error** under the message.
- Gemini does not see this whole notebook reliably: name your objects and columns in the prompt."""),
    *setup,
    md("## The task\n\nThe same text as `pi/TASK.md` in the RStudio half:\n\n" + TASK),
    md("""In Colab the files are read from the course repository. The next cell sets `data_dir`;
use `file.path(data_dir, "wdi_extract.csv")` wherever the task says `data/wdi_extract.csv`.
Here you work cell by cell instead of writing `clean_wdi.R`; the steps are the same."""),
    code("""data_dir <- if (dir.exists("data")) "data" else
  "https://raw.githubusercontent.com/umatter/pe_materials/main/b2/data"
cat(readLines(file.path(data_dir, "wdi_extract.csv"), n = 3), sep = "\\n")"""),
    *step("Step 1: read the file",
          "Read `wdi_extract.csv`, look at it, and drop the lines that are not data. "
          "Look at the last lines of the file first: what is there?",
          "Read the CSV file at file.path(data_dir, \"wdi_extract.csv\") with readr into `raw`. "
          "Drop the rows where `Series Code` is missing.",
          "raw"),
    md("### Self-check"),
    code("""stopifnot("Create the data frame `raw` first" = is.data.frame(raw),
          "raw should have 120 rows: 30 codes x 4 series" = nrow(raw) == 120,
          "raw should still have the column `Series Code`" = "Series Code" %in% names(raw))
cat("Step 1 passed.")"""),
    *step("Steps 2 and 3: missing values and long format",
          "Turn `..` into `NA`, reshape to one row per country, series and year, and make "
          "`year` an integer. Keep the numbers in a column called `value`.",
          "In the data frame `raw`, the columns 2015 [YR2015] to 2024 [YR2024] hold numbers, "
          "with \"..\" for missing values. Reshape to long format with tidyr into `long`, with an "
          "integer column `year` and a numeric column `value`.",
          "long"),
    md("### Self-check"),
    code("""stopifnot("Create the data frame `long` first" = exists("long") && is.data.frame(long),
          "long should have 1200 rows: 120 x 10 years" = nrow(long) == 1200,
          "year should be a number like 2015" = is.numeric(long$year) && all(long$year %in% 2015:2024),
          "value should be numeric (did the '..' become NA?)" = is.numeric(long$value),
          "some values should be NA" = anyNA(long$value))
cat("Steps 2 and 3 passed.")"""),
    *step("Steps 4 and 5: one column per series, units",
          "Spread the four series into columns (`gdp`, `population`, `unemployment`, "
          "`inflation`), then replace `gdp` by `gdp_bn` and add `gdp_pc`. Keep `iso3` "
          "(from `Country Code`) and `country`.",
          "Reshape `long` to wide so each Series Code is one column: NY.GDP.MKTP.CD -> gdp, "
          "SP.POP.TOTL -> population, SL.UEM.TOTL.ZS -> unemployment, FP.CPI.TOTL.ZG -> "
          "inflation. Rename Country Code to iso3 and Country Name to country. Then add gdp_bn "
          "= gdp in billions and gdp_pc = gdp / population, and drop gdp. Call it `wide`.",
          "wide"),
    md("### Self-check"),
    code("""stopifnot("Create the data frame `wide` first" = exists("wide") && is.data.frame(wide),
          "wide should have 300 rows: 30 codes x 10 years" = nrow(wide) == 300,
          "wide needs gdp_bn, gdp_pc, population, unemployment, inflation" =
            all(c("gdp_bn", "gdp_pc", "population", "unemployment", "inflation") %in% names(wide)),
          "gdp should be gone (replaced by gdp_bn)" = !"gdp" %in% names(wide))
cat("Steps 4 and 5 passed.")"""),
    *step("Step 6: join, keep countries, save",
          "Join `country_groups.csv`, keep only countries, clean the region names, put the "
          "columns in the order the task asks for, sort, and save `wdi_clean.csv`.",
          "Read file.path(data_dir, \"country_groups.csv\"). Join it to `wide` by iso3 = "
          "`Country Code` to add region (from Region) and income_group (from IncomeGroup). "
          "Keep only rows with a non-empty region, trim spaces in region, order the columns "
          "iso3, country, region, income_group, year, gdp_bn, population, gdp_pc, "
          "unemployment, inflation, sort by iso3 and year, and write it to wdi_clean.csv.",
          "clean"),
    md("### Final self-check\n\nThese checks use values from a reference solution."),
    code(FINAL_CHECK),
    md("""## Use the result

Ask Gemini for one plot of the cleaned data, for example GDP per person against unemployment in
2023, coloured by region. Is there anything in the plot that makes you doubt a cleaning step?"""),
    code(""),
    md("""## Before the break: notes for the debrief

Write down, in two or three lines each:

1. Which of Gemini's suggestions did you change or reject, and why?
2. Where was Gemini's first suggestion wrong, and how did you notice?
3. What did you check yourself that the self-checks did not?

## What this means for your project

Most of your project's time will go into data like this. An assistant makes each step faster,
but you still decide what a correct result is: write that down as checks before you ask."""),
]

write_notebook(cells, HERE / "02_data_handling_colab.ipynb")

# The pi half runs the same final checks on the file the agent produced.
(HERE / "pi" / "check.R").write_text(
    "# Checks wdi_clean.csv with the same tests as the Colab notebook.\n"
    "# Run in the folder that contains wdi_clean.csv:  Rscript pi/check.R\n"
    "# (generated by materials/b2/build.py; do not edit)\n"
    'clean <- read.csv("wdi_clean.csv", check.names = FALSE)\n'
    + FINAL_CHECK + "\n")
