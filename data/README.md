# Input data

`final_training_1260.csv` is the derived numerical training snapshot used for the
12 November 2026 refit. `final_inputs.json` contains the final index/volatility
inputs and public-source provenance without HTTP headers or authentication data.
`factor_catalog.csv` defines the report's revised 100-factor candidate set.

The 100-factor screening and 99-extension scripts require the original frozen
`revised_features100.csv`, which is intentionally supplied separately from this
code-focused repository. Put it under `data/local/`, or provide another absolute
path with `--features`. In the original project it is located at:

`sp500_pcr_model/outputs/screen100_revised_pool_post_result_2026-11-07/revised_features100.csv`

It must contain `date`, `target_date`, `issue_date`, `close`, `actual_close`,
`actual_return` and the factor identifiers in `factor_catalog.csv`.
Raw market feeds remain subject to their respective providers' terms.
