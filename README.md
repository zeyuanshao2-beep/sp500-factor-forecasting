# S&P 500 Factor Forecasting

This repository contains the code used to forecast the S&P 500 closing level six US trading sessions ahead. It covers factor screening, single-factor validation, two-factor extensions, and the final forecast presented in the accompanying report. The original project files are retained locally.

## Main Results

| Item | Result |
| --- | --- |
| Forecast origin | Market close on 12 November 2026 |
| Forecast target | Market close on 20 November 2026 |
| Final model | VIX3M/VIX; OLS with an intercept, fitted to 1,260 observations with realized six-session returns |
| Index level at the forecast origin | 7,592.40 |
| Forecast six-session return | 0.493% |
| Forecast closing level | **7,629.84** |

Calculations use full numerical precision. General numerical results in the report are displayed to three decimal places, and index levels to two decimal places.

## Reproduce the Final Forecast

Use Python 3.11 or later. The final forecast script uses only the Python standard library and can run offline:

```bash
python scripts/final_forecast.py
python -m unittest discover -s tests -v
```

The training factor dates run from 2021-10-28 to 2026-11-04. All 1,260 six-session target returns were realized on or before 2026-11-12. The script cross-checks the OLS coefficients using `statistics.linear_regression` and centered-moment formulas evaluated with 50-digit Decimal precision. It rejects training labels that had not been realized by the forecast origin.

## Factor Screening and Two-Factor Extensions

```bash
python -m pip install -r requirements.txt
python scripts/screen_factors.py --features data/local/revised_features100.csv
python scripts/two_factor_extension.py --features data/local/revised_features100.csv
```

The complete 100-factor input matrix is not included in this repository. See [data/README.md](data/README.md) for the required input format and its location in the original local project.

Each rolling fit uses the most recent 1,260 observations whose target returns were already realized at the corresponding forecast origin. All models are compared across the same 381 historical forecast origins. Factor rankings, predicted index levels, and summary results are written to `results/` without overwriting the inputs.

VIX3M/VIX achieves the lowest full-period single-factor MAPE, at 1.402%. The best two-factor extension adds the 30-year minus 10-year US Treasury yield spread, reducing MAPE to 1.384%, an improvement of 0.018 percentage points. However, the paired block-bootstrap 95% interval includes zero, including after adjustment for multiple comparisons. The simpler single-factor model is therefore retained.

The later 127 forecast origins overlap with the full-period screening sample. They provide a stability diagnostic rather than an independent holdout test. Factor screening and window comparisons are exploratory historical analyses; the lowest backtest error does not guarantee future performance.

## Repository Contents

- `src/forecasting.py`: Rolling OLS, error calculations, two-factor fitting, and block-bootstrap functions preserved from the original research scripts.
- `scripts/screen_factors.py`: Ranking of 100 single-factor models and benchmark comparisons over the later sample; corresponds to report Sections 5.1 and 5.2.
- `scripts/two_factor_extension.py`: Extensions that retain VIX3M/VIX and add each of the other 99 candidate factors; corresponds to report Section 5.3.
- `scripts/final_forecast.py`: Final OLS fit using 1,260 observations and the 20 November closing-level forecast; corresponds to report Section 5.4.
- `data/`: Factor definitions, the final training snapshot, and public-source provenance.
- `PROVENANCE.json`: SHA256 hashes of the original scripts and input files used to prepare this repository.

## Data and Provenance

The repository includes the research code and the final training snapshot needed to reproduce the final forecast. It excludes Word reports, conversation records, software runtimes, raw HTTP response headers, cookies, and account credentials.

The final forecast inputs are sourced from Yahoo Finance and Cboe; the detailed source URLs are recorded in `data/final_inputs.json`. Third-party data remain subject to their providers' terms, and this repository does not grant additional rights to those data.
