# Frozen input data

All calculations run offline. Raw provider response bodies are copied unchanged;
their SHA256 values and original retrieval times are in `source_manifest.json`.
HTTP cookies, authentication data and unrelated response headers are excluded.

- `frozen_market_history.csv`: archived price/VIX/VIX3M overlap plus later observations through 12 November 2026; includes raw ratio and six-session labels.
- `features100.csv.gz`: complete frozen derived matrix used for the report's 100-factor comparison. Pandas reads the gzip file directly.
- `factor_catalog.csv`: factor formulas, economic families, source labels and lag rules.
- `final_training_1260.csv`: exactly 1,260 mature pairs for the final refit.
- `final_inputs.json`: final close inputs and public source provenance.
- `availability_and_last_observations.json`: last usable observations and publication-time limitations.
- `raw/`: frozen Yahoo and Cboe response bodies, including the dated final quotes.

Observation dates, retrieval times, HTTP Last-Modified headers and first-publication
times are different concepts. Unverified publication vintages are explicitly marked;
no first-publication timestamp has been invented. Factor-catalog source labels identify
the additional public inputs underlying the frozen 100-factor matrix. Reconstructing
all 100 factors from raw options/Treasury feeds is outside this package; the complete
derived matrix is included so its forecasts and rankings are reproducible offline.
Third-party data remain subject to their providers' terms.
