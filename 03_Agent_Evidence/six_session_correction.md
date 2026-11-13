# Correction from five to six sessions

The original visible exchange (turns 95-97 in the excerpt JSON) records the user
identifying the cutoff error and asking for the code to be changed. A forecast
issued at 12:00 UTC on 13 November cannot use that day's US equity close.
The last eligible close is 12 November; the six subsequent sessions are
13, 16, 17, 18, 19 and 20 November 2026.

The target was changed to `P[t+6] / P[t] - 1`, coefficients and backtests were
re-estimated, and existing factor lookback windows were retained. The original
six-session design is preserved separately as historical evidence; its research
status and earlier factor definitions are not the final frozen model manifest.
Current verification checks the six-row target shift on the observed equity
calendar and rejects training labels dated after each forecast origin.
