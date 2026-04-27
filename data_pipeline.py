"""
data_pipeline.py
----------------
Shared data loading, cleaning, and analytical utilities for the
Mastercard Data Challenge finals analysis.

All three notebooks import from this module. Functions are organized by purpose:

  1. LOADERS        — Read and clean each raw dataset, returns tract-level DataFrame
  2. TRACT UTILS    — EOTR definition, crosswalk handling, FIPS standardization
  3. MERGE          — Build the canonical main analysis table
  4. STATS          — Correlation reporter with FDR correction, bootstrap Lasso,
                      effect-size helpers
  5. STYLE          — Plotting constants used across notebooks

Design notes
------------
- Every loader is defensive against ACS column-name variation.
- All FIPS codes are 11-character strings, zero-padded.
- `build_main()` is the single entry point for "give me the merged analysis table."
- The module is side-effect free except for writes to `datasets/` when explicitly
  invoked by a notebook.

Usage
-----
    from data_pipeline import build_main, CorrelationReporter, bootstrap_lasso
    main = build_main(data_dir="/content/datasets")
"""

import os
import re
import json
import warnings
from typing import Optional, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# Suppress sklearn warnings from our known-safe operations
warnings.filterwarnings('ignore', category=UserWarning)

# ────────────────────────────────────────────────────────────────
# 5. STYLE CONSTANTS
# ────────────────────────────────────────────────────────────────

ACCENT = "#2E75B6"
WEAK = "#C62828"
STRONG = "#2E7D32"
NEUTRAL = "#78909C"
EOTR_COLOR = "#D84315"
WOTR_COLOR = "#1565C0"

PLOT_RC = {
    'figure.figsize': (10, 6),
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'font.size': 11,
    'legend.fontsize': 10,
    'figure.dpi': 120
}

def apply_style():
    """Apply consistent plotting style. Call at the top of each notebook."""
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
    plt.rcParams.update(PLOT_RC)


# ────────────────────────────────────────────────────────────────
# 2. TRACT UTILS
# ────────────────────────────────────────────────────────────────

# 46 residential EOTR tracts (Wards 7 & 8 east of Anacostia).
# Military base (Joint Base Anacostia-Bolling) excluded.
EOTR_FIPS = [
    '11001007401','11001007403','11001007404','11001007406','11001007408',
    '11001007409','11001007502','11001007503','11001007504','11001007601',
    '11001007603','11001007604','11001007605','11001007703','11001007704',
    '11001007707','11001007708','11001007709','11001007803','11001007804',
    '11001007806','11001007807','11001007808','11001007809','11001009601',
    '11001009602','11001009603','11001009604','11001009700','11001009801',
    '11001009802','11001009803','11001009804','11001009807','11001009810',
    '11001009811','11001009906','11001009907','11001010100','11001010300',
    '11001010400','11001010500','11001010600','11001010700','11001010800'
]
EOTR_FIPS = sorted(set(EOTR_FIPS))
MILITARY_BASE_FIPS = '11001007301'


def standardize_fips(series: pd.Series) -> pd.Series:
    """Ensure FIPS codes are 11-character zero-padded strings."""
    return series.astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(11)


def _clean_acs_text(value: str) -> str:
    """Normalize ACS labels and headers by removing NBSPs and extra spaces."""
    return re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()


def _acs_tract_label_to_fips(value: str) -> Optional[str]:
    """Parse a DC ACS tract label into a standard 11-digit FIPS code."""
    text = _clean_acs_text(value)

    if re.fullmatch(r"\d{11}", text):
        return text

    match = re.search(r"Census Tract\s+([0-9]+(?:\.[0-9]+)?)", text, flags=re.IGNORECASE)
    if not match:
        return None

    tract_label = match.group(1)
    tract_code = tract_label.replace(".", "")
    if "." not in tract_label:
        tract_code = f"{tract_code}00"
    return f"11001{tract_code.zfill(6)}"


def _coerce_numeric(values: pd.Series) -> pd.Series:
    """Convert ACS-style numeric strings like '12,345', '-', or '**' to floats."""
    cleaned = values.astype(str).map(_clean_acs_text)
    cleaned = cleaned.str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace("$", "", regex=False)
    cleaned = cleaned.str.replace("%", "", regex=False)
    cleaned = cleaned.replace({"-": np.nan, "**": np.nan, "***": np.nan, "nan": np.nan, "None": np.nan})
    return pd.to_numeric(cleaned, errors='coerce')


def tag_region(df: pd.DataFrame, fips_col: str = 'Census Tract FIPS code') -> pd.DataFrame:
    """Add a 'region' column: 'EOTR' or 'Rest of DC'."""
    df = df.copy()
    df[fips_col] = standardize_fips(df[fips_col])
    df = df[df[fips_col] != MILITARY_BASE_FIPS].copy()
    df['region'] = np.where(df[fips_col].isin(EOTR_FIPS), 'EOTR', 'Rest of DC')
    return df


def load_tract_crosswalk(data_dir: str) -> pd.DataFrame:
    """Load the ACS tract-name to FIPS crosswalk."""
    path = os.path.join(data_dir, "DC_Neighborhoods_to_Census_Tracts_id.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    fips_col = next((c for c in df.columns if c.lower() == 'geoid' or 'fips' in c.lower()), None)
    if fips_col is None:
        fips_col = df.columns[0]
    name_col = next((c for c in df.columns if c.upper() == 'NAME'), None)
    if name_col is None:
        name_col = next((c for c in df.columns if 'tract' in c.lower() and 'name' in c.lower()), None)
    if name_col is None:
        name_col = df.columns[1]
    out = df[[name_col, fips_col]].copy()
    out.columns = ['acs_tract_name', 'Census Tract FIPS code']
    out['Census Tract FIPS code'] = standardize_fips(out['Census Tract FIPS code'])
    out['acs_tract_name'] = out['acs_tract_name'].map(_clean_acs_text)
    return out


# ────────────────────────────────────────────────────────────────
# 1. LOADERS
# ────────────────────────────────────────────────────────────────

def load_igs(data_dir: str) -> pd.DataFrame:
    """
    Load Mastercard IGS data, skipping metadata/definition sheets.
    """
    import os
    import pandas as pd
    import numpy as np

    # 1. Find the file
    igs_file = None
    for f in os.listdir(data_dir):
        if "Inclusive_Growth_Score" in f and (f.endswith(".xlsx") or f.endswith(".csv")):
            igs_file = f
            break

    if igs_file is None:
        raise FileNotFoundError("Inclusive Growth Score file not found in 'datasets/'")

    path = os.path.join(data_dir, igs_file)

    # 2. Load the data
    if igs_file.endswith(".csv"):
        # If it's a CSV, it might have metadata rows at the top
        # We'll try to find where the headers start
        igs = pd.read_csv(path)
        if "Definitions" in str(igs.columns[1]):
            # Re-read skipping the first few lines if the CSV has a header block
            igs = pd.read_csv(path, skiprows=2) 
    else:
        # If it's Excel, the data is almost always on sheet index 1
        # Sheet 0 is usually 'Definitions'
        try:
            igs = pd.read_excel(path, sheet_name=1) # Try the second sheet
            
            # Sanity check: if this sheet is empty or wrong, fall back to sheet 0
            if "tract" not in "".join(igs.columns).lower():
                igs = pd.read_excel(path, sheet_name=0, skiprows=2)
        except Exception:
            igs = pd.read_excel(path, sheet_name=0, skiprows=2)

    # 3. Clean headers
    igs.columns = [str(c).strip() for c in igs.columns]

    # 4. Find the FIPS column
    # Your specific header is 'Census Tract FIPS code'
    fips_col = next((c for c in igs.columns if "tract" in c.lower() or "fips" in c.lower()), None)

    if fips_col is None:
        raise ValueError(f"Still can't find Census Tract column. Found: {igs.columns.tolist()[:3]}")

    # 5. Standardize
    igs = igs.rename(columns={fips_col: "Census Tract FIPS code"})
    
    # Ensure year column exists
    year_col = next((c for c in igs.columns if "year" in c.lower()), None)
    if year_col:
        igs = igs.rename(columns={year_col: "Year"})
    else:
        igs["Year"] = 2023

    # Clean FIPS formatting
    igs["Census Tract FIPS code"] = (
        igs["Census Tract FIPS code"]
        .astype(str)
        .str.replace(r'\.0$', '', regex=True)
        .str.zfill(11)
    )

    # Keep only scores and IDs
    numeric_cols = igs.select_dtypes(include=[np.number]).columns.tolist()
    keep_cols = ["Census Tract FIPS code", "Year"] + [c for c in numeric_cols if c not in ["Census Tract FIPS code", "Year"]]
    igs = igs[keep_cols]

    # Tag region
    igs["region"] = np.where(
        igs["Census Tract FIPS code"].isin(EOTR_FIPS),
        "EOTR",
        "Rest of DC"
    )

    print(f"✅ Successfully loaded IGS data: {igs.shape}")
    return igs


def load_igs_tract_avg(data_dir: str) -> pd.DataFrame:
    """Load IGS and collapse to one row per tract (average across years).

    Returns a DataFrame with one row per tract and all score columns plus region.
    This is the base table that external data gets merged into.
    """
    igs = load_igs(data_dir)
    score_cols = [c for c in igs.columns if c not in ['Census Tract FIPS code','Year','region']
                  and igs[c].dtype in [np.float64, np.int64]]
    avg = (igs.groupby(['Census Tract FIPS code','region'], as_index=False)[score_cols]
              .mean())
    return avg


def _reshape_acs_wide(df: pd.DataFrame, label_col: str = 'Label (Grouping)') -> pd.DataFrame:
    """Convert a wide ACS table (tracts as columns) to long (one row per tract × category).

    Returns columns: acs_tract_name, label, value
    """
    estimate_cols = [c for c in df.columns if "!!Estimate" in c]
    if not estimate_cols:
        raise ValueError(f"No '!!Estimate' columns found. Columns: {df.columns[:5].tolist()}...")

    long = df.melt(id_vars=[label_col], value_vars=estimate_cols,
                    var_name='acs_col', value_name='value')
    long['acs_tract_name'] = long['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0].str.strip()
    long['value'] = pd.to_numeric(long['value'], errors='coerce')
    long['label'] = long[label_col].astype(str).str.strip()
    return long[['acs_tract_name','label','value']].dropna(subset=['acs_tract_name'])


def load_labor_market(data_dir: str) -> pd.DataFrame:
    """HUD Labor Market Engagement Index."""
    path = os.path.join(data_dir, "dc_labor_market_enagagement_index.csv")
    df = pd.read_csv(path)
    out = df[['GEOID','LBR_IDX']].copy()
    out.columns = ['Census Tract FIPS code','labor_market_index']
    out['Census Tract FIPS code'] = standardize_fips(out['Census Tract FIPS code'])
    return out


def load_median_income(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS median household income."""
    path = os.path.join(data_dir, "ACS_median_household_income.csv")
    df = pd.read_csv(path)
    estimate_cols = [c for c in df.columns if "!!Estimate" in c]
    # Row 0 typically contains the tract-level median; use flexible extraction
    row = df.iloc[0][estimate_cols].reset_index()
    row.columns = ['acs_col','median_household_income']
    row['acs_tract_name'] = row['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0].str.strip()
    row['median_household_income'] = pd.to_numeric(row['median_household_income'], errors='coerce')
    out = row.merge(crosswalk, on='acs_tract_name', how='left')
    return out[['Census Tract FIPS code','median_household_income']].dropna()


def load_poverty_share(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS income-to-poverty ratio → % below 1.0."""
    path = os.path.join(data_dir, "ACS_ratio_of_income_to_poverty_level.csv")
    df = pd.read_csv(path)
    long = _reshape_acs_wide(df)

    total = long[long['label'].str.contains('Total', case=False, na=False)].groupby('acs_tract_name')['value'].first()
    below = long[long['label'].isin(['Under .50', '.50 to .99'])].groupby('acs_tract_name')['value'].sum()

    out = pd.DataFrame({'below_poverty': below, 'total_pop': total})
    out['pct_below_poverty'] = 100 * out['below_poverty'] / out['total_pop']
    out = out.reset_index().merge(crosswalk, on='acs_tract_name', how='left')
    return out[['Census Tract FIPS code','pct_below_poverty']].dropna()


def load_gini(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS Gini index."""
    path = os.path.join(data_dir, "ACS_gini_index.csv")
    df = pd.read_csv(path)
    estimate_cols = [c for c in df.columns if "!!Estimate" in c]
    row = df.iloc[0][estimate_cols].reset_index()
    row.columns = ['acs_col','gini']
    row['acs_tract_name'] = row['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0].str.strip()
    row['gini'] = pd.to_numeric(row['gini'], errors='coerce')
    out = row.merge(crosswalk, on='acs_tract_name', how='left')
    return out[['Census Tract FIPS code','gini']].dropna()


def load_insurance(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS insurance coverage by employment status.

    Returns overall and labor-force uninsured rates. Uses percent-columns where
    available (most reliable); falls back to computed rates otherwise.
    """
    path = os.path.join(data_dir, "ACS_health_insurance_coverage_by_employment_status.csv")
    df = pd.read_csv(path)

    # Look for pre-computed percent columns first
    pct_cols = [c for c in df.columns if "Percent Estimate" in c and "Uninsured" in c]

    # Fallback: position-based pivot for count columns
    est_cols = [c for c in df.columns if "!!Estimate" in c and "Percent" not in c]
    if not est_cols and not pct_cols:
        raise ValueError("Could not find usable insurance columns")

    long = df.melt(id_vars=['Label (Grouping)'], value_vars=est_cols,
                    var_name='acs_col', value_name='value')
    long['acs_tract_name'] = long['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0].str.strip()
    long['value'] = pd.to_numeric(long['value'], errors='coerce')
    long['label'] = long['Label (Grouping)'].astype(str).str.strip()
    long = long.dropna(subset=['acs_tract_name'])

    # Row positions in ACS S2701 (verify against your file):
    # 0: Total civilian noninstitutionalized pop
    # 1-2: In labor force (total, employed)
    # 3: Unemployed
    # ... Uninsured counts typically appear in later positions
    # Most robust: compute by position within tract
    long['row_idx'] = long.groupby('acs_tract_name').cumcount()
    wide = long.pivot_table(index='acs_tract_name', columns='row_idx',
                             values='value', aggfunc='first').reset_index()

    # Defensive computation — adjust positions based on the ACS vintage
    try:
        wide['total_pop'] = wide[0]
        wide['total_uninsured'] = wide[3] if 3 in wide.columns else np.nan
        wide['lf_pop'] = wide[6] if 6 in wide.columns else np.nan
        wide['lf_uninsured'] = wide[9] if 9 in wide.columns else np.nan
        wide['overall_uninsured_rate'] = 100 * wide['total_uninsured'] / wide['total_pop']
        wide['labor_force_uninsured_rate'] = 100 * wide['lf_uninsured'] / wide['lf_pop']
    except Exception as e:
        wide['overall_uninsured_rate'] = np.nan
        wide['labor_force_uninsured_rate'] = np.nan

    out = wide[['acs_tract_name','overall_uninsured_rate','labor_force_uninsured_rate']]
    out = out.merge(crosswalk, on='acs_tract_name', how='left')
    return out[['Census Tract FIPS code','overall_uninsured_rate',
                'labor_force_uninsured_rate']].dropna(subset=['Census Tract FIPS code'])


def load_brfss(data_dir: str) -> pd.DataFrame:
    """CDC BRFSS PLACES tract-level health outcomes, 2023 snapshot.

    Returns one row per tract with health outcome columns.
    """
    path = os.path.join(data_dir, "brfss_dc_health_outcomes_data.csv")
    df = pd.read_csv(path)
    df = df[df['Year'] == 2023].copy()

    measure_map = {
        'Food insecurity in the past 12 months among adults': 'food_insecurity_pct',
        'Housing insecurity in the past 12 months among adults': 'housing_insecurity_pct',
        'Lack of reliable transportation in the past 12 months among adults': 'transportation_barrier_pct',
        'Utility services shut-off threat in the past 12 months among adults': 'utility_shutoff_pct',
        'Depression among adults': 'depression_pct',
        'Frequent mental distress among adults': 'mental_distress_pct',
        'Feeling socially isolated among adults': 'loneliness_pct',
        'Lack of social and emotional support among adults': 'lack_support_pct',
        'Diabetes among adults': 'diabetes_pct',
        'Obesity among adults': 'obesity_pct',
        'High blood pressure among adults': 'bp_pct',
        'Current asthma among adults': 'asthma_pct',
    }
    df['measure'] = df['Short_Question_Text'].map(measure_map)

    fips_col = next((c for c in df.columns if 'LocationID' in c or c.upper() == 'FIPS'), 'LocationID')
    df[fips_col] = standardize_fips(df[fips_col])

    wide = df.pivot_table(index=fips_col, columns='measure',
                           values='Data_Value', aggfunc='mean').reset_index()
    wide = wide.rename(columns={fips_col: 'Census Tract FIPS code'})
    return wide


def load_internet(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS internet subscription → broadband / disconnection rates."""
    path = os.path.join(data_dir, "ACS_internet_subscription_by_employment_status.csv")
    df = pd.read_csv(path)
    long = _reshape_acs_wide(df)

    total = long[long['label'] == 'Total:'].groupby('acs_tract_name')['value'].first()
    disc = long[long['label'].str.contains('No Internet access', case=False, na=False)].groupby('acs_tract_name')['value'].sum()
    bb = long[long['label'].str.contains('With a broadband Internet subscription', case=False, na=False)].groupby('acs_tract_name')['value'].sum()

    out = pd.DataFrame({'total_pop': total, 'disconnected': disc, 'broadband': bb}).reset_index()
    out['disconnected_rate'] = 100 * out['disconnected'] / out['total_pop']
    out['broadband_rate'] = 100 * out['broadband'] / out['total_pop']
    out = out.merge(crosswalk, on='acs_tract_name', how='left')
    return out[['Census Tract FIPS code','disconnected_rate','broadband_rate']].dropna()


def load_commute(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS travel time to work → long-commute rates."""
    path = os.path.join(data_dir, "ACS_time_to_work.csv")
    df = pd.read_csv(path)
    long = _reshape_acs_wide(df)

    total = long[long['label'] == 'Total:'].groupby('acs_tract_name')['value'].first()
    long45 = long[long['label'].isin(['45 to 59 minutes','60 to 89 minutes','90 or more minutes'])].groupby('acs_tract_name')['value'].sum()
    long60 = long[long['label'].isin(['60 to 89 minutes','90 or more minutes'])].groupby('acs_tract_name')['value'].sum()

    out = pd.DataFrame({'total_commuters': total,
                         'long_commute_45': long45,
                         'long_commute_60': long60}).reset_index()
    out['long_commute_rate'] = 100 * out['long_commute_45'] / out['total_commuters']
    out['very_long_commute_rate'] = 100 * out['long_commute_60'] / out['total_commuters']
    out = out.merge(crosswalk, on='acs_tract_name', how='left')
    return out[['Census Tract FIPS code','long_commute_rate','very_long_commute_rate']].dropna()


def load_food_access(data_dir: str) -> pd.DataFrame:
    """USDA Food Access Research Atlas (DC, urban half-mile measures)."""
    path = os.path.join(data_dir, "food_access_or_deserts_data_2019.xlsx")
    df = pd.read_excel(path, sheet_name="Food Access Research Atlas")
    dc = df[(df["State"] == "District of Columbia") & (df["County"] == "District of Columbia")].copy()
    dc['Census Tract FIPS code'] = standardize_fips(dc['CensusTract'])
    return dc[['Census Tract FIPS code','lapophalfshare','lalowihalfshare',
                'lahunvhalfshare','lasnaphalfshare']].copy()


def load_built_env(data_dir: str) -> pd.DataFrame:
    """DC Built Environment Indicators (proximity percentiles)."""
    path = os.path.join(data_dir, "Built_Environment_Indicators_proximity_to_metric.csv")
    df = pd.read_csv(path)
    df['Census Tract FIPS code'] = standardize_fips(df['Census ID'])
    keep = ['Census Tract FIPS code',
            'Driver 5: Transportation (percentiles)',
            'Driver 6: Food Environment (percentiles)',
            'Driver 7: Medical Care (percentiles)',
            'Overall Driver Score (percentiles)',
            '5.1: Proximity to Metro bus (percentiles)',
            '5.2: Proximity to Metro station (percentiles)',
            '6.1: Proximity to grocery stores (percentiles)',
            '7.1: Proximity to health care facilities (percentiles)',
            '7.2: Proximity to mental health facilities and providers (percentiles)']
    return df[[c for c in keep if c in df.columns]].copy()


def load_housing_burden(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS housing cost as % of income → cost-burden rate."""
    path = os.path.join(data_dir, "ACS_monthly_housing_costs_as_a_percentage_of_household_income.csv")
    df = pd.read_csv(path)
    long = _reshape_acs_wide(df)

    total = long[long['label'] == 'Total:'].groupby('acs_tract_name')['value'].first()
    burdened = long[long['label'].str.contains(r'30\.0 percent or more|30 percent or more',
                                                  case=False, na=False, regex=True)].groupby('acs_tract_name')['value'].sum()

    out = pd.DataFrame({'total_hh': total, 'burdened': burdened}).reset_index()
    out['housing_cost_burden_rate'] = 100 * out['burdened'] / out['total_hh']
    out = out.merge(crosswalk, on='acs_tract_name', how='left')
    return out[['Census Tract FIPS code','housing_cost_burden_rate']].dropna()


# ────────────────────────────────────────────────────────────────
# 3. MERGE — the canonical main analysis table
# ────────────────────────────────────────────────────────────────

def build_main(data_dir: str = "datasets", verbose: bool = True) -> pd.DataFrame:
    """Build the main analysis table by loading and merging every dataset."""
    msg = print if verbose else (lambda *a, **k: None)

    # Ensure directory exists
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    msg("🚀 Starting build_main...")
    
    # 1. Load IGS Base
    try:
        main = load_igs_tract_avg(data_dir)
    except Exception as e:
        msg(f"❌ CRITICAL FAILURE: Could not load IGS data. {e}")
        raise

    msg(f"📍 Base table: {len(main)} tracts ({(main['region']=='EOTR').sum()} EOTR)")

    # 2. Load Crosswalk for ACS loaders
    try:
        crosswalk = load_tract_crosswalk(data_dir)
    except Exception as e:
        msg(f"⚠️ Warning: Crosswalk failed to load. ACS merges may fail. {e}")
        crosswalk = pd.DataFrame(columns=['acs_tract_name', 'Census Tract FIPS code'])

    # 3. List of external datasets to merge
    merges = [
        ('HUD Labor', load_labor_market),
        ('ACS Income', lambda d: load_median_income(d, crosswalk)),
        ('ACS Poverty', lambda d: load_poverty_share(d, crosswalk)),
        ('ACS Gini', lambda d: load_gini(d, crosswalk)),
        ('ACS Insurance', lambda d: load_insurance(d, crosswalk)),
        ('BRFSS Health', load_brfss),
        ('ACS Internet', lambda d: load_internet(d, crosswalk)),
        ('ACS Commute', lambda d: load_commute(d, crosswalk)),
        ('USDA Food', load_food_access),
        ('DC Built Env', load_built_env),
        ('ACS Housing', lambda d: load_housing_burden(d, crosswalk)),
    ]

    for name, loader in merges:
        try:
            df = loader(data_dir)
            if df is not None and not df.empty:
                before_cols = main.shape[1]
                main = main.merge(df, on='Census Tract FIPS code', how='left')
                msg(f" ✅ {name:12} | +{main.shape[1] - before_cols} cols")
            else:
                msg(f" ⚠️ {name:12} | Empty dataframe")
        except Exception as e:
            msg(f" ❌ {name:12} | FAILED: {type(e).__name__}")

    msg(f"\nFinal Analysis Table: {main.shape[0]} tracts, {main.shape[1]} variables.")
    return main


# ────────────────────────────────────────────────────────────────
# 4. STATS UTILITIES
# ────────────────────────────────────────────────────────────────

# Runtime overrides for the finals workspace datasets. These keep the notebook
# interfaces stable while making the parsers match the files that are actually
# present on disk.

EOTR_FIPS = sorted([
    '11001007304', '11001007401', '11001007403', '11001007404', '11001007406',
    '11001007407', '11001007408', '11001007409', '11001007502', '11001007503',
    '11001007504', '11001007601', '11001007603', '11001007604', '11001007605',
    '11001007703', '11001007707', '11001007708', '11001007709', '11001007803',
    '11001007804', '11001007806', '11001007807', '11001007808', '11001007809',
    '11001009601', '11001009602', '11001009603', '11001009604', '11001009700',
    '11001009801', '11001009802', '11001009803', '11001009804', '11001009807',
    '11001009810', '11001009811', '11001009901', '11001009902', '11001009903',
    '11001009904', '11001009905', '11001009906', '11001009907', '11001010400',
    '11001010900'
])

def load_tract_crosswalk(data_dir: str) -> pd.DataFrame:
    """Load the ACS tract-name to FIPS crosswalk."""
    path = os.path.join(data_dir, "DC_Neighborhoods_to_Census_Tracts_id.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    fips_col = next((c for c in df.columns if c.lower() == 'geoid' or 'fips' in c.lower()), None)
    if fips_col is None:
        fips_col = df.columns[0]

    name_col = next((c for c in df.columns if c.upper() == 'NAME'), None)
    if name_col is None:
        name_col = next((c for c in df.columns if 'tract' in c.lower() and 'name' in c.lower()), None)
    if name_col is None:
        name_col = df.columns[1]

    out = df[[name_col, fips_col]].copy()
    out.columns = ['acs_tract_name', 'Census Tract FIPS code']
    out['acs_tract_name'] = out['acs_tract_name'].map(_clean_acs_text)
    out['Census Tract FIPS code'] = standardize_fips(out['Census Tract FIPS code'])
    return out


def load_igs(data_dir: str) -> pd.DataFrame:
    """Load Mastercard IGS data, skipping metadata and readme sheets."""
    candidates = []
    for preferred in ["igs.csv", "Inclusive_Growth_Score_Data_Export_16-03-2026_183818.xlsx"]:
        full_path = os.path.join(data_dir, preferred)
        if os.path.exists(full_path):
            candidates.append(full_path)

    for f in sorted(os.listdir(data_dir)):
        if "inclusive_growth_score" in f.lower() and f.lower().endswith((".xlsx", ".csv")):
            full_path = os.path.join(data_dir, f)
            if full_path not in candidates:
                candidates.append(full_path)

    if not candidates:
        raise FileNotFoundError("Inclusive Growth Score file not found in 'datasets/'")

    igs = None
    last_error = None
    for path in candidates:
        try:
            if path.lower().endswith(".csv"):
                candidate = pd.read_csv(path)
                if "Census Tract FIPS code" not in candidate.columns:
                    candidate = pd.read_csv(path, skiprows=2)
            else:
                xls = pd.ExcelFile(path)
                sheet_name = next((s for s in xls.sheet_names if "readme" not in s.lower()), xls.sheet_names[0])
                header_row = 1
                preview = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=5)
                for idx, row in preview.iterrows():
                    if row.astype(str).str.contains("Census Tract FIPS code", case=False, na=False).any():
                        header_row = idx
                        break
                candidate = pd.read_excel(path, sheet_name=sheet_name, header=header_row)

            candidate.columns = [str(c).strip() for c in candidate.columns]
            candidate = candidate.dropna(axis=1, how='all')
            candidate = candidate.drop(columns=[c for c in candidate.columns if c.lower().startswith("unnamed:")], errors='ignore')

            if any("tract" in c.lower() or "fips" in c.lower() for c in candidate.columns):
                igs = candidate
                break
        except Exception as exc:
            last_error = exc

    if igs is None:
        raise ValueError(f"Could not load IGS data from available files. Last error: {last_error}")

    fips_col = next((c for c in igs.columns if "tract" in c.lower() or "fips" in c.lower()), None)
    if fips_col is None:
        raise ValueError(f"Could not find Census Tract column. Found: {igs.columns.tolist()[:5]}")
    igs = igs.rename(columns={fips_col: "Census Tract FIPS code"})

    year_col = next((c for c in igs.columns if "year" in c.lower()), None)
    if year_col:
        igs = igs.rename(columns={year_col: "Year"})
    else:
        igs["Year"] = 2023

    igs = igs.dropna(subset=["Census Tract FIPS code"]).copy()
    igs["Census Tract FIPS code"] = standardize_fips(igs["Census Tract FIPS code"])
    igs["Year"] = pd.to_numeric(igs["Year"], errors='coerce').fillna(2023).astype(int)

    id_cols = {"Census Tract FIPS code", "Year", "County", "State", "region"}
    for col in igs.columns:
        if col not in id_cols:
            converted = _coerce_numeric(igs[col])
            if converted.notna().any():
                igs[col] = converted

    numeric_cols = [
        c for c in igs.columns
        if c not in ["Census Tract FIPS code", "Year"] and pd.api.types.is_numeric_dtype(igs[c])
    ]
    igs = igs[["Census Tract FIPS code", "Year"] + numeric_cols]
    igs = tag_region(igs)
    return igs


def load_igs_tract_avg(data_dir: str) -> pd.DataFrame:
    """Load IGS and collapse to one row per tract."""
    igs = load_igs(data_dir)
    score_cols = [
        c for c in igs.columns
        if c not in ['Census Tract FIPS code', 'Year', 'region']
        and pd.api.types.is_numeric_dtype(igs[c])
    ]
    return igs.groupby(['Census Tract FIPS code', 'region'], as_index=False)[score_cols].mean()


def _reshape_acs_wide(df: pd.DataFrame, label_col: str = 'Label (Grouping)') -> pd.DataFrame:
    """Convert a wide ACS table (tracts as columns) to long format."""
    estimate_cols = [c for c in df.columns if "!!Estimate" in c]
    if not estimate_cols:
        raise ValueError(f"No '!!Estimate' columns found. Columns: {df.columns[:5].tolist()}...")

    long = df.melt(id_vars=[label_col], value_vars=estimate_cols, var_name='acs_col', value_name='value')
    tract_labels = long['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0]
    long['acs_tract_name'] = tract_labels.map(_clean_acs_text)
    long['Census Tract FIPS code'] = tract_labels.map(_acs_tract_label_to_fips)
    long['label'] = long[label_col].map(_clean_acs_text)
    long['value'] = _coerce_numeric(long['value'])
    return long[['acs_tract_name', 'Census Tract FIPS code', 'label', 'value']].dropna(subset=['Census Tract FIPS code'])


def load_median_income(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS median household income."""
    path = os.path.join(data_dir, "ACS_median_household_income.csv")
    df = pd.read_csv(path)
    estimate_cols = [c for c in df.columns if "!!Estimate" in c]
    row = df.iloc[0][estimate_cols].reset_index()
    row.columns = ['acs_col', 'median_household_income']
    tract_labels = row['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0]
    row['acs_tract_name'] = tract_labels.map(_clean_acs_text)
    row['Census Tract FIPS code'] = tract_labels.map(_acs_tract_label_to_fips)
    row['median_household_income'] = _coerce_numeric(row['median_household_income'])
    if row['Census Tract FIPS code'].isna().any():
        row = row.drop(columns=['Census Tract FIPS code']).merge(crosswalk, on='acs_tract_name', how='left')
    return row[['Census Tract FIPS code', 'median_household_income']].dropna()


def load_poverty_share(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS income-to-poverty ratio -> percent below 1.0."""
    path = os.path.join(data_dir, "ACS_ratio_of_income_to_poverty_level.csv")
    long = _reshape_acs_wide(pd.read_csv(path))
    total = long[long['label'].str.contains('^Total', case=False, na=False)].groupby('Census Tract FIPS code')['value'].first()
    below = long[long['label'].isin(['Under .50', '.50 to .99'])].groupby('Census Tract FIPS code')['value'].sum()
    out = pd.DataFrame({'below_poverty': below, 'total_pop': total}).reset_index()
    out['pct_below_poverty'] = 100 * out['below_poverty'] / out['total_pop']
    return out[['Census Tract FIPS code', 'pct_below_poverty']].dropna()


def load_gini(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS Gini index."""
    path = os.path.join(data_dir, "ACS_gini_index.csv")
    df = pd.read_csv(path)
    estimate_cols = [c for c in df.columns if "!!Estimate" in c]
    row = df.iloc[0][estimate_cols].reset_index()
    row.columns = ['acs_col', 'gini']
    tract_labels = row['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0]
    row['acs_tract_name'] = tract_labels.map(_clean_acs_text)
    row['Census Tract FIPS code'] = tract_labels.map(_acs_tract_label_to_fips)
    row['gini'] = _coerce_numeric(row['gini'])
    if row['Census Tract FIPS code'].isna().any():
        row = row.drop(columns=['Census Tract FIPS code']).merge(crosswalk, on='acs_tract_name', how='left')
    return row[['Census Tract FIPS code', 'gini']].dropna()


def load_insurance(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS insurance coverage by employment status."""
    path = os.path.join(data_dir, "ACS_health_insurance_coverage_by_employment_status.csv")
    df = pd.read_csv(path)
    est_cols = [c for c in df.columns if "!!Estimate" in c and "Percent" not in c]
    if not est_cols:
        raise ValueError("Could not find usable insurance columns")

    long = df.melt(id_vars=['Label (Grouping)'], value_vars=est_cols, var_name='acs_col', value_name='value')
    tract_labels = long['acs_col'].str.extract(r'^(Census Tract [^!]+)')[0]
    long['Census Tract FIPS code'] = tract_labels.map(_acs_tract_label_to_fips)
    long['label'] = long['Label (Grouping)'].map(_clean_acs_text)
    long['value'] = _coerce_numeric(long['value'])
    long = long.dropna(subset=['Census Tract FIPS code'])
    long['row_idx'] = long.groupby('Census Tract FIPS code').cumcount()

    wide = long.pivot_table(index='Census Tract FIPS code', columns='row_idx', values='value', aggfunc='first').reset_index()

    total_pop = wide[0] if 0 in wide.columns else np.nan
    labor_force_pop = wide[1] if 1 in wide.columns else np.nan
    employed_uninsured = wide[6] if 6 in wide.columns else np.nan
    unemployed_uninsured = wide[11] if 11 in wide.columns else np.nan
    nilf_uninsured = wide[16] if 16 in wide.columns else np.nan

    wide['overall_uninsured_rate'] = 100 * (employed_uninsured + unemployed_uninsured + nilf_uninsured) / total_pop
    wide['labor_force_uninsured_rate'] = 100 * (employed_uninsured + unemployed_uninsured) / labor_force_pop

    return wide[['Census Tract FIPS code', 'overall_uninsured_rate', 'labor_force_uninsured_rate']].dropna(subset=['Census Tract FIPS code'])


def load_brfss(data_dir: str) -> pd.DataFrame:
    """CDC BRFSS PLACES tract-level health outcomes, 2023 snapshot."""
    path = os.path.join(data_dir, "brfss_dc_health_outcomes_data.csv")
    df = pd.read_csv(path)
    df = df[df['Year'] == 2023].copy()

    patterns = {
        'food_insecurity_pct': ['food insecurity'],
        'housing_insecurity_pct': ['housing insecurity'],
        'transportation_barrier_pct': ['transportation barrier', 'lack of reliable transportation'],
        'utility_shutoff_pct': ['utility services', 'shut-off threat'],
        'depression_pct': ['depression'],
        'mental_distress_pct': ['frequent mental distress'],
        'loneliness_pct': ['loneliness', 'socially isolated'],
        'lack_support_pct': ['lack of social/emotional support', 'lack of social and emotional support'],
        'diabetes_pct': ['diabetes'],
        'obesity_pct': ['obesity'],
        'bp_pct': ['high blood pressure'],
        'asthma_pct': ['asthma'],
    }

    search_text = (
        df['Short_Question_Text'].fillna('').astype(str)
        + ' | '
        + df['Measure'].fillna('').astype(str)
    ).str.lower()

    def _map_brfss_measure(text: str) -> Optional[str]:
        for target, needles in patterns.items():
            if any(needle in text for needle in needles):
                return target
        return None

    df['measure'] = search_text.map(_map_brfss_measure)
    df = df[df['measure'].notna()].copy()

    fips_col = next((c for c in df.columns if 'LocationID' in c or c.upper() == 'FIPS'), 'LocationID')
    df[fips_col] = standardize_fips(df[fips_col])
    wide = df.pivot_table(index=fips_col, columns='measure', values='Data_Value', aggfunc='mean').reset_index()
    return wide.rename(columns={fips_col: 'Census Tract FIPS code'})


def load_internet(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS internet subscription -> broadband / disconnection rates."""
    path = os.path.join(data_dir, "ACS_internet_subscription_by_employment_status.csv")
    long = _reshape_acs_wide(pd.read_csv(path))
    total = long[long['label'] == 'Total:'].groupby('Census Tract FIPS code')['value'].first()
    disconnected = long[long['label'].str.contains('Without an Internet subscription|No Internet access|No computer',
                                                   case=False, na=False, regex=True)].groupby('Census Tract FIPS code')['value'].sum()
    broadband = long[long['label'].str.contains('With a broadband Internet subscription',
                                                case=False, na=False)].groupby('Census Tract FIPS code')['value'].sum()
    out = pd.DataFrame({'total_pop': total, 'disconnected': disconnected, 'broadband': broadband}).reset_index()
    out['disconnected_rate'] = 100 * out['disconnected'] / out['total_pop']
    out['broadband_rate'] = 100 * out['broadband'] / out['total_pop']
    return out[['Census Tract FIPS code', 'disconnected_rate', 'broadband_rate']].dropna()


def load_commute(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS travel time to work -> long-commute rates."""
    path = os.path.join(data_dir, "ACS_time_to_work.csv")
    long = _reshape_acs_wide(pd.read_csv(path))
    total = long[long['label'] == 'Total:'].groupby('Census Tract FIPS code')['value'].first()
    long45 = long[long['label'].isin(['45 to 59 minutes', '60 to 89 minutes', '90 or more minutes'])].groupby('Census Tract FIPS code')['value'].sum()
    long60 = long[long['label'].isin(['60 to 89 minutes', '90 or more minutes'])].groupby('Census Tract FIPS code')['value'].sum()
    out = pd.DataFrame({'total_commuters': total, 'long_commute_45': long45, 'long_commute_60': long60}).reset_index()
    out['long_commute_rate'] = 100 * out['long_commute_45'] / out['total_commuters']
    out['very_long_commute_rate'] = 100 * out['long_commute_60'] / out['total_commuters']
    return out[['Census Tract FIPS code', 'long_commute_rate', 'very_long_commute_rate']].dropna()


def load_housing_burden(data_dir: str, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """ACS housing cost as percent of income -> cost-burden rate."""
    path = os.path.join(data_dir, "ACS_monthly_housing_costs_as_a_percentage_of_household_income.csv")
    df = pd.read_csv(path)
    long = _reshape_acs_wide(df)
    long['row_idx'] = long.groupby('Census Tract FIPS code').cumcount()

    wide = long.pivot_table(index='Census Tract FIPS code', columns='row_idx', values='value', aggfunc='first').reset_index()
    total_hh = wide[0] if 0 in wide.columns else np.nan
    no_cash_rent = wide[48] if 48 in wide.columns else 0
    burdened = sum(wide[idx] for idx in [30, 34, 38, 42, 46] if idx in wide.columns)
    at_risk_denominator = total_hh - no_cash_rent

    wide['housing_cost_burden_rate'] = 100 * burdened / at_risk_denominator
    wide.loc[at_risk_denominator <= 0, 'housing_cost_burden_rate'] = np.nan
    out = wide[['Census Tract FIPS code', 'housing_cost_burden_rate']]
    return out[['Census Tract FIPS code', 'housing_cost_burden_rate']].dropna()


def build_main(data_dir: str = "datasets", verbose: bool = True) -> pd.DataFrame:
    """Build the main analysis table by loading and merging every dataset."""
    msg = print if verbose else (lambda *a, **k: None)

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    msg("Starting build_main...")

    try:
        main = load_igs_tract_avg(data_dir)
    except Exception as e:
        msg(f"[CRITICAL] Could not load IGS data: {e}")
        raise

    msg(f"Base table: {len(main)} tracts ({(main['region'] == 'EOTR').sum()} EOTR)")

    try:
        crosswalk = load_tract_crosswalk(data_dir)
    except Exception as e:
        msg(f"[WARN] Crosswalk failed to load. ACS merges may fail: {e}")
        crosswalk = pd.DataFrame(columns=['acs_tract_name', 'Census Tract FIPS code'])

    merges = [
        ('HUD Labor', load_labor_market),
        ('ACS Income', lambda d: load_median_income(d, crosswalk)),
        ('ACS Poverty', lambda d: load_poverty_share(d, crosswalk)),
        ('ACS Gini', lambda d: load_gini(d, crosswalk)),
        ('ACS Insurance', lambda d: load_insurance(d, crosswalk)),
        ('BRFSS Health', load_brfss),
        ('ACS Internet', lambda d: load_internet(d, crosswalk)),
        ('ACS Commute', lambda d: load_commute(d, crosswalk)),
        ('USDA Food', load_food_access),
        ('DC Built Env', load_built_env),
        ('ACS Housing', lambda d: load_housing_burden(d, crosswalk)),
    ]

    for name, loader in merges:
        try:
            df = loader(data_dir)
            if df is not None and not df.empty:
                before_cols = main.shape[1]
                main = main.merge(df, on='Census Tract FIPS code', how='left')
                msg(f" [OK] {name:12} | +{main.shape[1] - before_cols} cols")
            else:
                msg(f" [WARN] {name:12} | Empty dataframe")
        except Exception as e:
            msg(f" [FAIL] {name:12} | {type(e).__name__}: {e}")

    msg(f"\nFinal Analysis Table: {main.shape[0]} tracts, {main.shape[1]} variables.")
    return main


class CorrelationReporter:
    """Accumulates correlation tests and applies FDR correction at the end.

    Usage:
        r = CorrelationReporter()
        r.test(df, 'x', 'y', label='X vs Y')
        summary_df = r.summary(alpha=0.05)
    """

    def __init__(self, method: str = 'spearman'):
        self.results = []
        self.method = method

    def test(self, df: pd.DataFrame, x: str, y: str, label: Optional[str] = None):
        valid = df[[x, y]].dropna()
        if len(valid) < 5:
            return None
        if self.method == 'spearman':
            rho, p = stats.spearmanr(valid[x], valid[y])
        else:
            rho, p = stats.pearsonr(valid[x], valid[y])
        self.results.append({
            'Test': label or f"{x} vs {y}",
            'n': int(len(valid)),
            'rho': float(rho),
            'p': float(p)
        })
        return rho, p

    def summary(self, alpha: float = 0.05) -> pd.DataFrame:
        if not self.results:
            return pd.DataFrame()
        from statsmodels.stats.multitest import multipletests
        df = pd.DataFrame(self.results)
        reject, p_adj, _, _ = multipletests(df['p'].values, alpha=alpha, method='fdr_bh')
        df['p_adj (BH)'] = p_adj
        df['survives FDR'] = reject
        for c in ['rho','p','p_adj (BH)']:
            df[c] = df[c].round(4)
        return df


def rank_biserial(group_a: np.ndarray, group_b: np.ndarray,
                   alternative: str = 'less') -> Tuple[float, float]:
    """Mann-Whitney U test with rank-biserial correlation effect size.

    Returns (r_rb, p_value). r_rb ranges from -1 to 1.
    """
    u, p = stats.mannwhitneyu(group_a, group_b, alternative=alternative)
    r_rb = 1 - (2 * u) / (len(group_a) * len(group_b))
    return r_rb, p


def bootstrap_lasso(X: np.ndarray, y: np.ndarray, alpha: float,
                     n_bootstrap: int = 1000, random_state: int = 42) -> Dict:
    """Bootstrap Lasso to estimate coefficient stability.

    Returns a dict with per-feature retention frequency and CI on coefficients.
    """
    from sklearn.linear_model import Lasso
    from sklearn.utils import resample

    n, p = X.shape
    coefs = np.zeros((n_bootstrap, p))
    retained = np.zeros(p)
    rng = np.random.default_rng(random_state)

    for b in range(n_bootstrap):
        idx = resample(np.arange(n), n_samples=n, random_state=rng.integers(0, 1e6))
        Xb, yb = X[idx], y[idx]
        try:
            lb = Lasso(alpha=alpha, max_iter=20000)
            lb.fit(Xb, yb)
            coefs[b] = lb.coef_
            retained += (np.abs(lb.coef_) > 1e-6).astype(int)
        except Exception:
            coefs[b] = np.nan

    return {
        'retention_freq': retained / n_bootstrap,
        'median_coef': np.nanmedian(coefs, axis=0),
        'ci_lower': np.nanpercentile(coefs, 2.5, axis=0),
        'ci_upper': np.nanpercentile(coefs, 97.5, axis=0),
        'all_coefs': coefs
    }


# ────────────────────────────────────────────────────────────────
# Findings registry — single source of truth across notebooks
# ────────────────────────────────────────────────────────────────

FINDINGS_PATH = "findings.json"


def save_finding(key: str, value, path: str = FINDINGS_PATH):
    """Write a single finding to the shared JSON registry.

    Converts numpy types to Python scalars for JSON compatibility.
    """
    def _clean(v):
        if isinstance(v, (np.floating,)): return float(v)
        if isinstance(v, (np.integer,)): return int(v)
        if isinstance(v, np.ndarray): return v.tolist()
        if isinstance(v, dict): return {k: _clean(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)): return [_clean(x) for x in v]
        return v

    try:
        with open(path, 'r') as f:
            findings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        findings = {}

    findings[key] = _clean(value)
    with open(path, 'w') as f:
        json.dump(findings, f, indent=2)


def load_findings(path: str = FINDINGS_PATH) -> dict:
    """Load all findings written so far."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ────────────────────────────────────────────────────────────────
# Convenience: full feature list for ML
# ────────────────────────────────────────────────────────────────

ML_FEATURES = [
    'Economy',
    'Labor Market Engagement Index Score',
    'Commercial Diversity Score',
    'New Businesses Score',
    'Small Business Loans Score',
    'Internet Access Score',
    'Travel Time to Work Score',
    'Affordable Housing Score',
    'Health Insurance Coverage Score',
    'Gini Coefficient Score',
]

ML_TARGET = 'food_insecurity_pct'

BRFSS_OUTCOMES = [
    'food_insecurity_pct', 'housing_insecurity_pct', 'transportation_barrier_pct',
    'utility_shutoff_pct', 'depression_pct', 'mental_distress_pct',
    'loneliness_pct', 'lack_support_pct'
]

ECONOMIC_ANCHORS = [
    'Economy', 'Labor Market Engagement Index Score',
    'Inclusive Growth Score', 'pct_below_poverty'
]

PROXIMITY_MEASURES = [
    ('USDA: % pop >0.5mi supermarket', 'lapophalfshare', '+'),
    ('USDA: % low-inc >0.5mi', 'lalowihalfshare', '+'),
    ('USDA: % no-vehicle >0.5mi', 'lahunvhalfshare', '+'),
    ('DC BE: Medical Care proximity pctile', 'Driver 7: Medical Care (percentiles)', '−'),
    ('DC BE: Healthcare facility proximity', '7.1: Proximity to health care facilities (percentiles)', '−'),
    ('DC BE: Mental health facility proximity', '7.2: Proximity to mental health facilities and providers (percentiles)', '−'),
    ('DC BE: Grocery proximity pctile', '6.1: Proximity to grocery stores (percentiles)', '−'),
    ('DC BE: Metro bus proximity', '5.1: Proximity to Metro bus (percentiles)', '−'),
    ('DC BE: Metro station proximity', '5.2: Proximity to Metro station (percentiles)', '−'),
]
