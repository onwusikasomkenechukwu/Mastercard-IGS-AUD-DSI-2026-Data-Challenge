# Mastercard Data Science Challenge Finals — Restructured Deliverables

## What's in this folder

| File | Purpose |
|---|---|
| `data_pipeline.py` | Shared module — data loading, cleaning, statistical utilities. Both notebooks import from it. |
| `01_findings.ipynb` | **Pitch-facing findings.** The three paradoxes with robustness tests. Run this first. |
| `02_evidence_chain.ipynb` | **Full methodological defense.** External validation, FDR-corrected correlations, bootstrap Lasso, deployment prioritization. |
| `03_pitch_appendix.ipynb` | **Q&A cheatsheet.** One cell per anticipated judge question with answer + chart. Keep open on a second screen during the pitch. |
| `PITCH_DECK_STRUCTURE.md` | Slide-by-slide deck structure with speaker notes, timing, team assignments. |

## Why this structure

The original 5-notebook structure was built for linear reading — data-source by data-source. That serves a written report, not a live pitch. This restructure is built around the three audiences that actually matter:

- **Notebook 1 is for judges** who might glance at the notebooks to check the headline claims. Three paradoxes, three charts, three robustness tests. Five minutes of scrolling gets them the whole argument.

- **Notebook 2 is for methodology reviewers** who want the full defense. Every statistical choice is justified in-line. Every limitation is stated in §G.

- **Notebook 3 is for you, during Q&A.** Each cell is one anticipated question with the answer and the supporting chart ready to display. When a judge asks "what about your R²?", you don't improvise — you scroll to Q1, read the number off the screen.

## How to run

### Setup (once)

```bash
pip install numpy pandas matplotlib seaborn scipy statsmodels scikit-learn openpyxl
```

Place `data_pipeline.py` and all three notebooks in the same directory. The notebooks look for `/content/datasets/` (Colab default) — edit the `DATA_DIR` constant at the top of each notebook if your data is elsewhere.

### Run order

```
Notebook 1 → Notebook 2 → Notebook 3
```

Notebook 1 builds and caches `datasets/main_analysis.csv`. Notebook 2 reads the cache, runs the full analysis, and writes `bootstrap_stability.csv`, `top10_deployment.csv`, `lasso_vs_ridge.csv`, `findings.json`. Notebook 3 reads those outputs and produces the Q&A reference.

If you change the data and want to rebuild from scratch, delete `datasets/main_analysis.csv` and re-run Notebook 1.

### Expected run times

- Notebook 1: ~30 seconds (first run, ~5 seconds after cache exists)
- Notebook 2: ~2 minutes (bootstrap Lasso with 1000 resamples is the longest step)
- Notebook 3: ~5 seconds

## What's different from the original submission

### 1. Three paradoxes as the framing

The original deck emphasized "EOTR has low IGS scores → needs business investment." That framing is:
- Not surprising to judges
- Not Mastercard-specific (any funder could do it)
- Not tied to a concrete intervention

The restructure leads with three counterintuitive findings that reframe the problem space. The intervention falls out of the findings rather than being bolted on.

### 2. ML fixed

The original Lasso returned `NaN` R² because LeaveOneOut CV is mathematically undefined with single-point validation sets. Notebook 2 §E uses 5-fold CV (stable R²), adds a held-out test set, runs 1000 bootstrap resamples to measure coefficient stability, and adds Ridge as a sensitivity check for multicollinearity. All three are standard practice and all were missing.

### 3. Gini is reported honestly

In the original, Gini Coefficient Score was the Lasso's largest coefficient and the decision tree's first split — and was omitted from the deck. The restructure keeps it and reframes why it supports rather than undermines the business-linkage story.

### 4. Multiple testing correction

Original analysis ran dozens of correlation tests without FDR correction. Restructure applies Benjamini-Hochberg across every test family and reports which findings survive.

### 5. DC-wide as primary, EOTR as confirmation

Original restricted most analyses to 46 EOTR tracts, giving poor statistical power. Restructure uses all ~180 DC residential tracts for primary analysis, treats EOTR findings as consistency checks.

### 6. Deployment prioritization

Original deck said "pilot in EOTR" without specifying where. Restructure produces a Need × Readiness ranking identifying the top 5 tracts for Phase 1 launch — a concrete, defensible target.

## What to check after you run it

### Critical numbers for the pitch

These need to be valid numbers, not `NaN`:

1. **Lasso 5-fold CV R²** (from Notebook 2 §E2) — the answer to "what's your out-of-sample validity?"
2. **Bootstrap retention frequencies** (Notebook 2 §E4) — the answer to "how stable are your coefficients?"
3. **Proximity paradox ρ values** (Notebook 1 §Paradox 1C) — the anchor of the pitch
4. **Time-cost gap in hours** (Notebook 1 §Paradox 3A) — the anchor number for Slide 2
5. **Top 5 deployment tract FIPS codes** (Notebook 2 §F1) — the named tracts for Slide 7

Paste these values into the deck before pitch day.

### Likely failure points

In order of probability:

1. **ACS column names** — different ACS vintages use slightly different headers. The loaders in `data_pipeline.py` use flexible column detection but may still miss edge cases. If a loader fails, the error will be localized to that dataset.
2. **Insurance row positions** — the ACS S2701 table uses position-based pivoting with defensive fallbacks. If `overall_uninsured_rate` comes back nonsensical (all zeros, all 100s), adjust the row indices in `load_insurance()`.
3. **SBA designation column detection** — varies significantly by export vintage. Present but defensive in the module.

### Quick sanity checks

- `main.shape` should be approximately `(180, 50+)` — 180 tracts, 50+ columns
- `(main['region']=='EOTR').sum()` should be `46`
- `main['food_insecurity_pct'].describe()` should give mean around 25%, max around 55%
- `main['Inclusive Growth Score'].describe()` should give mean around 50 (DC-benchmarked)

## One honest caveat

I couldn't execute these against your real data — you don't have the CSVs shared yet. The code is written to match the structure of your original pipeline, but you'll be the one who verifies the final numbers. The methodology is correct; the specific values (exact CV R², exact bootstrap percentages, exact top-5 FIPS codes) come from your run.

If something breaks when you run it, send the traceback and I'll fix it. Most likely fixes are localized column-name patches in `data_pipeline.py`.

## For the pitch deck

`PITCH_DECK_STRUCTURE.md` is the slide-by-slide structure document. It includes:

- 10 slides + 2 appendix slides with full content and visuals
- Speaker notes for each slide (what to actually say, word-by-word-ish)
- Timing budget totaling 6:35 + 1:25 buffer = 8:00
- Three-person speaker assignments
- Pre-pitch checklist
- What-not-to-say language guide
- Fallback phrases for "I don't know"

Hand this to whoever's building slides (or work from it yourself).

## Contact during the run

If anything breaks or needs adjustment, the fastest path is:

1. Copy the full error traceback
2. Tell me which notebook and which cell failed
3. I can edit `data_pipeline.py` or the relevant notebook cell — you don't need to restart analysis

Good luck in the finals.
