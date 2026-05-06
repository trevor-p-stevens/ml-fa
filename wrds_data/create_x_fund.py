import pandas as pd
import numpy as np
from tqdm import tqdm

tqdm.pandas()

df = pd.read_csv("wrds_data/merged.gz", compression="gzip", nrows=5)
print(df.columns)
df = pd.read_csv("wrds_data/stock_price.gz", compression="gzip", nrows=5)
print(df.columns)
df = pd.read_csv("wrds_data/fundamental_quarterly.gz", compression="gzip", nrows=5)
print(df.columns)

#load data sets
fundq = pd.read_csv("wrds_data/fundamental_quarterly.gz", compression="gzip")
print("fundq done")

fundq = fundq.copy()

# Gross Profit
fundq["gpq"] = fundq["revtq"] - fundq["cogsq"]

# EBIT (Compustat best proxy already provided)
fundq["ebitq"] = fundq["oiadpq"]

# EBITDA
fundq["ebitdaq"] = fundq["oiadpq"] + fundq["dpq"]

fundq = fundq.sort_values(["gvkey", "datadate"]).copy()

fundq["gross_margin"] = fundq["gpq"] / fundq["revtq"]
fundq["operating_margin"] = fundq["oiadpq"] / fundq["revtq"]
fundq["net_margin"] = fundq["niq"] / fundq["revtq"]
fundq["ebitda_margin"] = fundq["ebitdaq"] / fundq["revtq"]

g = fundq.groupby("gvkey")
fundq["rev_qoq"] = g["revtq"].pct_change(1, fill_method=None)
fundq["rev_yoy"] = g["revtq"].pct_change(4, fill_method=None)
fundq["ni_qoq"] = g["niq"].pct_change(1, fill_method=None)
fundq["ni_yoy"] = g["niq"].pct_change(4, fill_method=None)
fundq["eps_qoq"] = g["epsfxq"].pct_change(1, fill_method=None)
fundq["eps_yoy"] = g["epsfxq"].pct_change(4, fill_method=None)
fundq["ebitda_qoq"] = g["ebitdaq"].pct_change(1, fill_method=None)
fundq["ebitda_yoy"] = g["ebitdaq"].pct_change(4, fill_method=None)
fundq["rev_accel"] = fundq["rev_qoq"] - g["rev_qoq"].shift(1)
fundq["ni_accel"] = fundq["ni_qoq"] - g["ni_qoq"].shift(1)

fundq["rd_ratio"] = fundq["xrdq"] / fundq["revtq"]
fundq["sga_ratio"] = fundq["xsgaq"] / fundq["revtq"]
fundq["opex_ratio"] = fundq["xoprq"] / fundq["revtq"]
fundq["cogs_ratio"] = fundq["cogsq"] / fundq["revtq"]
fundq["revenue_growth"] = fundq["rev_qoq"]
fundq["opex_growth"] = g["xoprq"].pct_change(1, fill_method=None)
fundq["efficiency_trend"] = fundq["revenue_growth"] - fundq["opex_growth"]

fundq["da_ratio"] = fundq["dpq"] / fundq["revtq"]

fundq["ebit_ebitda_gap"] = (fundq["ebitdaq"] - fundq["ebitq"]) / fundq["revtq"]

fundq["ni_oiadp_gap"] = (fundq["niq"] - fundq["oiadpq"]) / fundq["revtq"]

fundq["eps"] = fundq["epsfxq"]

fundq["shares_growth"] = g["cshoq"].pct_change(1, fill_method=None)

fundq["dilution_rate"] = fundq["shares_growth"]
fundq["eps_vs_ni_growth_gap"] = fundq["eps_qoq"] - fundq["ni_qoq"]

fundq["tax_rate"] = fundq["txtq"] / fundq["piq"]

fundq["non_op_ratio"] = (fundq["piq"] - fundq["oiadpq"]) / fundq["revtq"]

fundq["one_time_effect"] = fundq["niq"] - fundq["oiadpq"]

fundq["log_revenue"] = np.log1p(fundq["revtq"].clip(lower=0))
fundq["log_ebitda"] = np.log1p(fundq["ebitdaq"].clip(lower=0))

fundq["log_net_income"] = np.log1p(fundq["niq"].abs())
fundq["ni_sign"] = np.sign(fundq["niq"])

feature_cols = [
    # margins
    "gross_margin", "operating_margin", "net_margin", "ebitda_margin",

    # growth
    "rev_qoq", "rev_yoy", "ni_qoq", "ni_yoy",
    "eps_qoq", "eps_yoy", "ebitda_qoq", "ebitda_yoy",
    "rev_accel",

    # efficiency
    "rd_ratio", "sga_ratio", "opex_ratio", "cogs_ratio", "efficiency_trend",

    # earnings quality
    "da_ratio", "ebit_ebitda_gap", "ni_oiadp_gap",

    # dilution
    "dilution_rate", "eps_vs_ni_growth_gap",

    # tax
    "tax_rate", "non_op_ratio", "one_time_effect",

    # scale
    "log_revenue", "log_ebitda", "log_net_income"
]

X_fundq = fundq[["gvkey", "datadate", "rdq"] + feature_cols]

print("Finished X_fundq")

X_fundq["event_date"] = pd.to_datetime(X_fundq["rdq"], errors="coerce") + pd.Timedelta(days=1)

# fallback for missing rdq
X_fundq["event_date"] = X_fundq["event_date"].fillna(
    pd.to_datetime(X_fundq["datadate"], errors="coerce") + pd.Timedelta(days=45)
)

print("Standardize column names")
X_fundq.columns = X_fundq.columns.str.lower()

print("Saving X_fund")

X_fundq.to_csv("X_fundq.csv.gz", index=True, compression="gzip")
print("X_fundq saved to 'X_fundq.csv.gz'")