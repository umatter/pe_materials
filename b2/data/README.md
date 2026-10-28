# Data for Block 2

| File | Content |
|---|---|
| `wdi_extract.csv` | 26 countries and 4 aggregates (World, European Union, Euro area, Sub-Saharan Africa), 2015–2024, four series: GDP (current US$), population, unemployment (% of labour force, modelled ILO estimate), inflation (consumer prices, annual %) |
| `country_groups.csv` | Region and income group of each code; aggregates have an empty region |

**Source:** World Bank, World Development Indicators, retrieved on 28 October 2026 through the
World Bank API (`api.worldbank.org/v2`). The files have the layout of a WDI DataBank download:
one column per year, `..` for missing values, notes at the end of the file. The values are
unchanged.

**Licence:** [Creative Commons Attribution 4.0 (CC BY 4.0)](https://datacatalog.worldbank.org/public-licenses#cc-by).
Cite as: World Bank (2026), *World Development Indicators*.

`build_data.R` rebuilds both files from the API. You do not need it for the exercise.
