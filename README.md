# S&P 500 Factor Forecasting Evidence Package

This repository contains the frozen data, portable Python code, agent evidence,
historical results and figures for the report's six-session S&P 500 forecast.
All numerical reproduction uses the supplied snapshots and requires no network access.

## Frozen forecast

| Item | Value |
| --- | --- |
| Origin | Close on 12 November 2026 |
| Target | Official S&P 500 price-index close on 20 November 2026, 16:00 New York / 21:00 UTC |
| Information cutoff | 13 November 2026, 12:00 London / UTC, 07:00 New York |
| Model | VIX3M/VIX; OLS with intercept; 1,260 mature training pairs |
| Origin index level | 7,592.40 |
| Predicted six-session return | 0.493% |
| Final forecast | **7,629.84 index points** |

`final_forecast.json` records full-precision inputs and coefficients, target/cutoff
times, the six future sessions and a SHA256-linked check against the submitted PDF cover.

## Repository structure

- `01_Data/`: frozen S&P 500, VIX and VIX3M source bodies; source URLs, original retrieval times, publication-time limitations and last usable observations; complete compressed 100-factor matrix and exact final training sample.
- `02_Code/`: factor construction, rolling OLS, screening/backtests, second-factor bootstrap, independent verification and final refit.
- `03_Agent_Evidence/`: selected original prompts/responses, six-session correction and separately labelled current execution/tool receipts.
- `04_Results/`: rankings, 381 historical forecasts, regression evidence, benchmarks, bootstrap intervals and verification receipts.
- `05_Figures/`: original regression scatterplot, actual-versus-forecast chart, final refit and editable workflow diagrams.

## Software and installation

Python 3.11 or later. Exact versions used for this package are in
`02_Code/software_versions.json`; `requirements.txt` pins NumPy, pandas and timezone data.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux, instead:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Reproduction commands

Run these commands from the repository root:

```bash
# Final forecast: Python standard library only
python 02_Code/final_forecast.py
python -m unittest discover -s 02_Code/tests -v

# Rebuild the ratio and targets from frozen market data
python 02_Code/construct_factor.py

# All 100 single-factor models on the same 381 historical origins
python 02_Code/screen_factors.py

# All 99 two-factor extensions and paired/multiple-comparison bootstrap
python 02_Code/two_factor_extension.py

# Reproduce 3/5/10-year windows, benchmarks and block-bootstrap comparisons
python 02_Code/window_benchmarks.py

# Independent standard-library verification of all 381 selected-model fits
python 02_Code/verify_package.py
```

New calculations are written to `reproduced_results/`; archived inputs and results
are not overwritten. Screening should select VIX3M/VIX within the report's revised
100-factor matrix (MAPE 1.402%). Benchmarks have MAPEs 1.440% and 1.491%; the later
127-origin MAPEs are 1.267%, 1.338% and 1.364%. The best two-factor extension adds
the 30-year minus 10-year Treasury spread (MAPE 1.384%); its paired 95% difference
interval spans zero. The final script should return `final_forecast: "7629.84"`
and `independent_decimal_check: "PASS"`. Verification should report `PASS`.

## Interpretation and evidence limits

The report uses the archived revised 100-factor candidate matrix. Rankings are
conditional on that candidate set and the historical dates examined. The later
127 origins overlap the full screening sample and provide a stability diagnostic,
not an untouched holdout. Six-session errors overlap; block-bootstrap comparisons
are conditional exploratory checks. Original publication/correction vintages have
not been fully verified. Numerical reproducibility does not establish availability
of every original historical input or future forecast accuracy.

Original prompt/response excerpts, selected original tool calls extracted from the
archived rollout, and current reproduction receipts are identified separately.
Only whitelisted tool records are included; private reasoning, system/developer
messages and unrelated conversations are excluded. Diagrams document the workflow;
they are not original screenshots. Human approval is not inferred or fabricated.

Raw options/Treasury feeds for constructing every candidate are not included; the
complete frozen derived matrix is supplied for offline ranking reproduction.
Provider response bodies retain their original bytes. Public metadata omit cookies,
credentials and unrelated headers. Third-party data remain subject to provider terms.
