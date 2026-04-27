# Mastercard IGS & AUC DSI Data Challenge — Finale Repository
**Team Data Benders | Howard University**
**Project: CAN — Community Action Network**

---

## What this project is

CAN is a Mastercard-anchored two-sided platform proposal that turns IGS data into local opportunity in low-IGS DC communities. Residents see their community's economic gaps, start small businesses to fill them with AI-powered planning support, and stakeholders fund and hire from what they see — all measured through Mastercard's existing IGS infrastructure.

The repository contains the full analytical backbone, the pitch deliverables, and the supporting documentation that took us from a midpoint submission to the Atlanta finale.

---

## What's in this folder

### Pitch deliverables (presented in Atlanta)

| File | Purpose |
|---|---|
| `Final_Pitch.pptx` | The 10-slide finale deck. Walks the data-to-platform argument across the prescribed rubric structure. |
| `FINALE_SCRIPT_PATH_B.md` | Word-for-word delivery script for all 10 slides, with timing, hand-offs, and Q&A bank. |
| `Judge_Leave-Behind.pptx` | One-page leave-behind for the judging panel. Headline paradox, named tracts, ask, and contact info. |
| `pitch_support_pack.md` | Deeper Q&A answers, scaling answers ($1M / $0M), fresh-eye review, and bad-Q&A recovery plan. |

### Prototype

| File | Purpose |
|---|---|
| `CAN_prototype/` | Figma Make build of the CAN platform. Five interactive screens: Landing / Role Selection, Community Pulse, Opportunity Map, Stakeholder Dashboard, Impact Dashboard. Used as visual evidence on Slide 7. |

### Analytical backbone

| File | Purpose |
|---|---|
| `data_pipeline.py` | Shared module — data loading, cleaning, statistical utilities. All three notebooks import from it. |
| `01_findings.ipynb` | Pitch-facing findings. The proximity paradox and the economic-friction reframe with robustness tests. Run this first. |
| `02_evidence_chain.ipynb` | Full methodological defense. External validation, FDR-corrected correlations, bootstrap Lasso, deployment prioritization. |
| `03_pitch_appendix.ipynb` | Q&A cheatsheet — one cell per anticipated judge question with answer and chart. Open on a second screen during Q&A. |

### Reference

| File | Purpose |
|---|---|
| `Team97_DataBenders_Howard_University.pdf` | Midpoint submission. Submitted in March, used for pitch-stop evaluation, advanced us to the finale. |
| `2026_Data_Challenge_Overview___Guidelines.pdf` | Official challenge documentation. Reference for the prescribed 10-slide rubric structure. |

---

## How the project evolved

The repository reflects three stages of work:

1. **Midpoint submission** (March 16). Pitched a three-layer "Community Health Access Network" — health, food, and digital layers. Advanced to finale on the strength of the analytical work, not the solution coherence.

2. **Telehealth-pilot reframe** (March – mid-April). Restructured around the proximity paradox finding: highest-need EOTR tracts are physically closer to healthcare than lower-need tracts. Reframed the binding constraint as economic and time friction, not geographic distance. Proposed merchant-hosted telehealth booths as the wedge.

3. **Path B / CAN platform pivot** (final week). Built a working Figma Make prototype of a two-sided platform that operationalizes the analysis directly: residents start the small businesses their communities need, stakeholders fund what they see, and Mastercard's IGS infrastructure measures impact. The platform is what we presented at the finale.

The analytical work in the notebooks is constant across all three stages — what changed is the proposed intervention. Bootstrap stability analysis identified labor-market engagement, small-business loans, travel time, internet access, and affordable housing as the stable predictors of food insecurity. Those are economic and inclusive-growth conditions, not service-delivery problems. CAN is the response that addresses those signals at the source.

---

## How to run the notebooks

### Setup (once)

```bash
pip install numpy pandas matplotlib seaborn scipy statsmodels scikit-learn openpyxl
```

Place `data_pipeline.py` and all three notebooks in the same directory. The notebooks look for `/content/datasets/` (Colab default) — edit the `DATA_DIR` constant at the top of each notebook if data is elsewhere.

### Run order

```
Notebook 1 → Notebook 2 → Notebook 3
```

Notebook 1 builds and caches `datasets/main_analysis.csv`. Notebook 2 reads the cache, runs the full analysis, and writes `bootstrap_stability.csv`, `top10_deployment.csv`, `lasso_vs_ridge.csv`, `findings.json`. Notebook 3 reads those outputs and produces the Q&A reference.

To rebuild from scratch, delete `datasets/main_analysis.csv` and re-run Notebook 1.

### Expected run times

- Notebook 1: ~30 seconds (first run; ~5 seconds after cache exists)
- Notebook 2: ~2 minutes (bootstrap Lasso with 1000 resamples is the longest step)
- Notebook 3: ~5 seconds

---

## What's different from the midpoint submission

### 1. The intervention is a two-sided platform, not a three-layer service stack

The midpoint proposed Health, Food, and Digital service layers as separate-but-related interventions. That answer hedges across three solutions instead of committing to one. CAN commits: residents form the businesses their communities need, stakeholders find them, and Mastercard's data infrastructure makes both sides visible to each other.

### 2. ML fixed

The midpoint analysis had a Lasso model returning `NaN` R² because LeaveOneOut CV is mathematically undefined with single-point validation sets. Notebook 2 §E uses 5-fold CV (stable R² = 0.69), adds a held-out test set (R² = 0.61), runs 1000 bootstrap resamples to measure coefficient stability, and adds Ridge as a sensitivity check for multicollinearity. All four were missing from the midpoint version.

### 3. Multiple testing correction

The midpoint ran dozens of correlation tests without FDR correction. The current analysis applies Benjamini-Hochberg across every test family and reports which findings survive.

### 4. DC-wide as primary, EOTR as confirmation

The midpoint restricted most analyses to 46 EOTR tracts, giving poor statistical power. The current analysis uses all 205 DC residential tracts for primary modeling, with EOTR findings treated as consistency checks.

### 5. The proximity paradox is the headline finding

Across 18 specifications testing whether physical distance to facilities predicts food insecurity in EOTR, 14 of 18 point the wrong way for any policy built on geographic proximity. This is the analytical anchor for the platform pivot — the binding constraint is not geographic, so the intervention cannot be a fixed-location service. CAN, as a digital platform that surfaces opportunity gaps to residents, addresses the actual constraint.

### 6. Deployment is named, not gestured at

The midpoint proposed "pilot in EOTR." The finale identifies five specific Phase-1 deployment tracts using a Need-by-Readiness ranking: 96.02, 78.08, 75.03, 74.08, 74.03. Approximately 16,281 residents in the initial focus set.

### 7. Rubric alignment

The midpoint deck and the early finale draft used a pitch-craft structure (cold open, reframe, intervention, ask). The current deck uses the official rubric structure — Title, Objective, Community Overview, IGS Benchmarking, Key Findings, Healthcare Access Context, Proposed Small-Business Solutions, Implementation, Metrics, Conclusion — while preserving the analytical sharpness of the earlier framing.

---

## What to verify after running the notebooks

### Numbers that appear on the deck

These need to be valid (not `NaN`) and consistent between the notebooks and the slides:

1. **Lasso 5-fold CV R² and held-out R²** (Notebook 2 §E2 and §E3) — used on Slide 5
2. **Bootstrap retention frequencies for the top 5 features** (Notebook 2 §E4) — used on Slide 5 bar chart (100%, 99.7%, 96.7%, 92%, 90.3%)
3. **Proximity paradox top-10 vs bottom-10 statistics** (Notebook 1 §Paradox 1) — Slide 2 anchor (48.3% vs 21.9%, 0.57 vs 0.31, "14 of 18 tests")
4. **Top 5 deployment tract FIPS codes** (Notebook 2 §F1) — Slide 4 map markers
5. **EOTR community totals** — 46 tracts, 16,281 residents in top 5, 46.2% average food insecurity

If any of these come back as NaN or different values, fix the deck before pitch day.

### Likely failure points

In order of probability:

1. **ACS column names.** Different ACS vintages use slightly different headers. The loaders in `data_pipeline.py` use flexible column detection but may miss edge cases. Failures localize to specific dataset loaders.
2. **Insurance row positions.** The ACS S2701 table uses position-based pivoting with defensive fallbacks. If `overall_uninsured_rate` comes back nonsensical, adjust row indices in `load_insurance()`.
3. **SBA designation column detection.** Varies by export vintage. Defensive logic exists in the module but may need tweaks.

### Quick sanity checks

- `main.shape` should be approximately `(205, 50+)` — 205 tracts, 50+ columns
- `(main['region']=='EOTR').sum()` should be `46`
- `main['food_insecurity_pct'].describe()` should give mean ~25%, max ~55%
- `main['Inclusive Growth Score'].describe()` should give mean around 50 (DC-benchmarked)
- Bootstrap stability output should show 5 features with retention >90%

---

## Repository hygiene

- All notebooks have been validated end-to-end against the cached `main_analysis.csv`.
- The Figma Make prototype is hosted; static screenshots used in `Final_Pitch.pptx` slide 7 are exported from the April 27, 2026 build.
- Numbers displayed on prototype screens (47 businesses, $445K funding, 89 jobs, 1,247 families) are mock pilot targets, adopted as CAN year-1 goals on Slide 9. This disclosure appears in the slide footer.
- The closing slide cites a ~20-year DC neighborhood life-expectancy gap from the DC Health 2024 Health Systems Plan. Source on file.

---

## Acknowledgements

Datasets used: Mastercard Inclusive Growth Score, ACS 5-Year, CDC BRFSS PLACES, USDA Food Access Atlas, DC Built Environment Indicators, HRSA MUA Designations, SBA Census Tract Designations, HUD Labor Market Index, DC Health 2024 Health Systems Plan.

Team: Somkenechukwu Onwusika, Oritsejemiyotan Atsagbede, Moyinoluwa Ogunjobi.
Howard University.

Submitted to the 2026 Mastercard IGS & AUC DSI Data Challenge — Atlanta Finale, April 30 – May 2, 2026.
