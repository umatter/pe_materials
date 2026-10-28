# Build data/imdb_sample.csv: 100 short IMDB movie reviews, 50 positive and
# 50 negative, with the human (gold) label.
# Source: the test split of the Large Movie Review Dataset (Maas et al. 2011),
# as published on Hugging Face (stanfordnlp/imdb). Run from materials/b4/:
#   Rscript make_sample.R

url <- paste0("https://huggingface.co/datasets/stanfordnlp/imdb/resolve/main/",
              "plain_text/test-00000-of-00001.parquet")
path <- tempfile(fileext = ".parquet")
download.file(url, path, mode = "wb", quiet = TRUE)
imdb <- as.data.frame(nanoparquet::read_parquet(path))

imdb$id <- sprintf("imdb_test_%05d", seq_len(nrow(imdb)))
imdb$text <- trimws(gsub("\\s+", " ", gsub("<br\\s*/?>", " ", imdb$text)))
imdb$label <- ifelse(imdb$label == 1, "positive", "negative")

# Short reviews only: easier to read in class, and cheaper to label.
words <- lengths(strsplit(imdb$text, " ", fixed = TRUE))
short <- imdb[words >= 30 & words <= 150, ]

set.seed(42)
pos <- short[short$label == "positive", ]
neg <- short[short$label == "negative", ]
sample <- rbind(pos[sample(nrow(pos), 50), ], neg[sample(nrow(neg), 50), ])
sample <- sample[sample(nrow(sample)), c("id", "text", "label")]

dir.create("data", showWarnings = FALSE)
write.csv(sample, "data/imdb_sample.csv", row.names = FALSE)
cat("Wrote", nrow(sample), "reviews:", table(sample$label), "(neg, pos)\n")
