# imdb_sample.csv

100 short English movie reviews with a human sentiment label, used in the Block 4 notebook to
check LLM labels against human ones.

| Column | Content |
|---|---|
| `id` | `imdb_test_<row>`: row number in the test split of the source (1-based) |
| `text` | The review; HTML line breaks (`<br />`) replaced by spaces |
| `label` | Human (gold) label: `positive` or `negative` |

**Sample.** Reviews of 30–150 words from the test split, then 50 positive and 50 negative drawn
at random (`set.seed(42)`) and shuffled. `../make_sample.R` rebuilds the file from the source.

**Source.** Large Movie Review Dataset v1.0 (Maas et al. 2011), test split, as published on
Hugging Face: <https://huggingface.co/datasets/stanfordnlp/imdb>. The gold label comes from the
reviewer's own star rating on IMDb (≤ 4 of 10 negative, ≥ 7 of 10 positive), not from coders.

**Licence and citation.** The dataset is published by its authors for research use
(<https://ai.stanford.edu/~amaas/data/sentiment/>) and asks users to cite:

> Andrew L. Maas, Raymond E. Daly, Peter T. Pham, Dan Huang, Andrew Y. Ng and Christopher Potts.
> 2011. Learning Word Vectors for Sentiment Analysis. *Proceedings of the 49th Annual Meeting of
> the Association for Computational Linguistics*, 142–150.

The review texts were written by IMDb users. Use this sample for teaching and research only.
