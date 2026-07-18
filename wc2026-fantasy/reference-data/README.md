# Reference data

Source research that informed the scoring model and player pool. These files are **not read
by the pipeline at runtime** — the engine pulls live data over HTTP — they're kept for
provenance and to show the underlying research.

- `*.xlsx` — scoring-stat spreadsheets (WC 2022, WC qualifying, international friendlies)
  used to calibrate the FIFA scoring constants in `wc_scout/scoring.py`.
- `WorldCupSquads.txt` — the 48-nation squad lists.
