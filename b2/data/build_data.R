# Rebuilds the two exercise files from the World Bank API, in the shape of a
# World Development Indicators DataBank export (".." for missing values,
# one column per year, footer lines). You do not need to run this.
#   Rscript build_data.R   (run inside materials/b2/data/)

countries <- c("CHE", "DEU", "FRA", "ITA", "AUT", "GBR", "USA", "CAN", "MEX",
               "BRA", "ARG", "CHN", "JPN", "KOR", "IND", "IDN", "AUS", "ZAF",
               "NGA", "EGY", "TUR", "SAU", "RUS", "VEN", "AFG", "SSD")
aggregates <- c("WLD", "EUU", "EMU", "SSF")
series <- c("NY.GDP.MKTP.CD", "SP.POP.TOTL", "SL.UEM.TOTL.ZS", "FP.CPI.TOTL.ZG")
years <- 2015:2024

wb <- function(path) {
  httr2::request(paste0("https://api.worldbank.org/v2/", path)) |>
    httr2::req_url_query(format = "json", per_page = 20000) |>
    httr2::req_perform() |>
    httr2::resp_body_json(simplifyVector = TRUE)
}

codes <- c(countries, aggregates)
rows <- list()
for (s in series) {
  d <- wb(sprintf("country/%s/indicator/%s?date=%d:%d",
                  paste(codes, collapse = ";"), s, min(years), max(years)))[[2]]
  d <- d[d$countryiso3code %in% codes, ]
  for (cc in codes) {
    x <- d[d$countryiso3code == cc, ]
    vals <- vapply(years, function(y) {
      v <- x$value[x$date == as.character(y)]
      if (length(v) == 0 || is.na(v)) ".." else format(v, digits = 15, scientific = FALSE)
    }, character(1))
    row <- data.frame(`Country Name` = x$country$value[1], `Country Code` = cc,
                      `Series Name` = x$indicator$value[1], `Series Code` = s,
                      check.names = FALSE)
    row[paste0(years, " [YR", years, "]")] <- as.list(vals)
    rows[[length(rows) + 1]] <- row
  }
}
wdi <- do.call(rbind, rows)
wdi <- wdi[order(wdi$`Country Name`, match(wdi$`Series Code`, series)), ]

out <- "wdi_extract.csv"
write.csv(wdi, out, row.names = FALSE, na = "")
# DataBank exports end with two empty lines and two notes
cat(',,,,\n,,,,\nData from database: World Development Indicators,,,,\n',
    sprintf('Last Updated: %s,,,,\n', format(Sys.Date(), "%m/%d/%Y")),
    file = out, append = TRUE, sep = "")

# Country metadata, as in the "Metadata - Countries" sheet of a WDI download:
# aggregates have an empty Region and IncomeGroup.
meta <- wb("country")[[2]]
meta <- meta[meta$id %in% codes, ]
is_agg <- meta$region$value == "Aggregates"
groups <- data.frame(`Country Code` = meta$id,
                     Region = ifelse(is_agg, "", meta$region$value),
                     IncomeGroup = ifelse(is_agg, "", meta$incomeLevel$value),
                     TableName = meta$name,
                     check.names = FALSE)
groups <- groups[order(groups$`Country Code`), ]
write.csv(groups, "country_groups.csv", row.names = FALSE, na = "")
