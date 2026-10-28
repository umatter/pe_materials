# Task: clean a World Bank extract

Two files in `data/`:

- `wdi_extract.csv`: a download from the World Bank's World Development Indicators for 26 countries
  and 4 aggregates (World, European Union, …), 2015–2024, four series.
- `country_groups.csv`: region and income group of each code.

Write an R script `clean_wdi.R` that produces `wdi_clean.csv` in six steps:

1. **Read** `wdi_extract.csv`. Drop the lines at the end that are not data (they have no `Series Code`).
2. **Missing values** are coded as `..`. Turn them into `NA` and make the year columns numeric.
3. **Long format:** one row per country, series and year. `year` is an integer (`2015`, not
   `2015 [YR2015]`).
4. **One column per series**, named by its `Series Code`: `NY.GDP.MKTP.CD` → `gdp`,
   `SP.POP.TOTL` → `population`, `SL.UEM.TOTL.ZS` → `unemployment`, `FP.CPI.TOTL.ZG` → `inflation`.
5. **Units:** replace `gdp` (current US$) by `gdp_bn`, GDP in billions of US$, and add `gdp_pc`,
   GDP per person in US$.
6. **Join** `country_groups.csv` to add `region` and `income_group`. Keep countries only: the
   aggregates have an empty region. Remove stray spaces at the ends of the region names.

Result: one row per country and year, sorted by `iso3` and `year`, with the columns
`iso3, country, region, income_group, year, gdp_bn, population, gdp_pc, unemployment, inflation`.
Save it as `wdi_clean.csv`.

Use base R or the tidyverse (`readr`, `dplyr`, `tidyr`). Do not change the files in `data/`.
