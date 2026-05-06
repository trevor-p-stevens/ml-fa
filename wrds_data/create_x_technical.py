import pandas as pd
import numpy as np
from tqdm import tqdm

tqdm.pandas()

# df = pd.read_csv("wrds_data/stock_price.gz", compression="gzip", nrows=5)
# print(df.columns)

# dsf = pd.read_csv("wrds_data/stock_price.gz", compression="gzip", low_memory=False)

# for col in ["PRC", "RET", "VOL"]:
#     if col in dsf.columns:
#         dsf[col] = pd.to_numeric(dsf[col], errors="coerce")

# dsf["PRC"] = dsf["PRC"].abs()
# print("dsf done")

# dsf = dsf.sort_values(["PERMNO", "date"]).copy()

# dsf["PRC"] = dsf["PRC"].abs()
# dsf["RET"] = pd.to_numeric(dsf["RET"], errors="coerce").fillna(0)
# dsf["VOL"] = pd.to_numeric(dsf["VOL"], errors="coerce").fillna(0)

# g = dsf.groupby("PERMNO")

# dsf["sma50"] = g["PRC"].progress_transform(lambda x: x.rolling(50).mean())
# dsf["sma100"] = g["PRC"].progress_transform(lambda x: x.rolling(100).mean())
# dsf["sma200"] = g["PRC"].progress_transform(lambda x: x.rolling(200).mean())

# dsf["ema50"] = g["PRC"].progress_transform(lambda x: x.ewm(span=50).mean())
# dsf["ema100"] = g["PRC"].progress_transform(lambda x: x.ewm(span=100).mean())
# dsf["ema200"] = g["PRC"].progress_transform(lambda x: x.ewm(span=200).mean())
# dsf["dist_sma200"] = (dsf["PRC"] - dsf["sma200"]) / dsf["sma200"]
# dsf["trend_slope_50"] = g["PRC"].progress_transform(
#     lambda x: x.rolling(50).apply(lambda y: np.polyfit(range(len(y)), y, 1)[0])
# )
# dsf["sma_cross"] = (dsf["sma50"] > dsf["sma200"]).astype(int)

# print("finished trend indicators")
# dsf.to_csv("dsf.csv.gz", index=True, compression="gzip")
# print("Saved after trend indicators")


# dsf["ret_3m"] = g["RET"].progress_transform(lambda x: (1+x).rolling(63).apply(np.prod) - 1)
# dsf["ret_6m"] = g["RET"].progress_transform(lambda x: (1+x).rolling(126).apply(np.prod) - 1)
# dsf["ret_12m"] = g["RET"].progress_transform(lambda x: (1+x).rolling(252).apply(np.prod) - 1)

# mkt = dsf.groupby("date")["RET"].transform("mean")
# dsf["resid_mom"] = dsf["ret_12m"] - mkt
# print("Finished momentum features")
# dsf.to_csv("dsf.csv.gz", index=True, compression="gzip")
# print("Saved after momentum")

# def rsi(series, n=14):
#     delta = series.diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)

#     avg_gain = gain.rolling(n).mean()
#     avg_loss = loss.rolling(n).mean()

#     rs = avg_gain / avg_loss
#     return 100 - (100 / (1 + rs))

# dsf["rsi14"] = g["PRC"].progress_transform(lambda x: rsi(x, 14))
# dsf["rsi28"] = g["PRC"].progress_transform(lambda x: rsi(x, 28))

# high = g["PRC"].progress_transform(lambda x: x.rolling(14).max())
# low  = g["PRC"].progress_transform(lambda x: x.rolling(14).min())

# dsf["williams_r"] = (high - dsf["PRC"]) / (high - low)
# dsf["stoch"] = (dsf["PRC"] - low) / (high - low)

# print("Finshed Oscillators")
# dsf.to_csv("dsf.csv.gz", index=True, compression="gzip")
# print("Saved after oscillators")

# dsf["vol30"] = g["RET"].progress_transform(lambda x: x.rolling(30).std())
# dsf["vol90"] = g["RET"].progress_transform(lambda x: x.rolling(90).std())

# dsf["downside_vol"] = g["RET"].progress_transform(
#     lambda x: x[x < 0].rolling(30).std()
# )

# mkt_ret = dsf.groupby("date")["RET"].transform("mean")

# def beta(x, m):
#     return x.rolling(60).cov(m) / m.rolling(60).var()

# dsf["beta"] = beta(dsf["RET"], mkt_ret)

# print("Finished Volatillity and risk")
# dsf.to_csv("dsf.csv.gz", index=True, compression="gzip")
# print("Saved after vol and risk")

# dsf["vol_sma"] = g["VOL"].progress_transform(lambda x: x.rolling(30).mean())

# dsf["vol_spike"] = dsf["VOL"] / dsf["vol_sma"]
# dsf["price_vol"] = dsf["PRC"] * dsf["VOL"]

# print("finsiehd volume")
# dsf.to_csv("dsf.csv.gz", index=True, compression="gzip")
# print("Saved after volume")

# ema12 = g["PRC"].progress_transform(lambda x: x.ewm(span=12).mean())
# ema26 = g["PRC"].progress_transform(lambda x: x.ewm(span=26).mean())

# dsf["macd"] = ema12 - ema26
# dsf["macd_signal"] = dsf.groupby("PERMNO")["macd"].progress_transform(lambda x: x.ewm(span=9).mean())
# dsf["macd_hist"] = dsf["macd"] - dsf["macd_signal"]

# dsf["adx_proxy"] = dsf["PRC"].diff().abs().rolling(14).mean()

# print("Finsihed trend strength")
# dsf.to_csv("dsf.csv.gz", index=True, compression="gzip")
# print("Saved after trend strength")
# Define technical feature columns
# Define technical feature columns
technical_feature_cols = [
    # Trend indicators
    "sma50", "sma100", "sma200",
    "ema50", "ema100", "ema200",
    "dist_sma200", "trend_slope_50", "sma_cross",

    # Momentum
    "ret_3m", "ret_6m", "ret_12m", "resid_mom",

    # Oscillators
    "rsi14", "rsi28", "williams_r", "stoch",

    # Volatility & Risk
    "vol30", "vol90", "downside_vol", "beta",

    # Volume & Flow
    "vol_sma", "vol_spike", "price_vol",

    # Trend Strength
    "macd", "macd_signal", "macd_hist", "adx_proxy"
]

# Define the columns to keep
columns_to_keep = ["PERMNO", "date", "PRC", "RET", "VOL"] + technical_feature_cols

# Process the final DataFrame in chunks
chunk_size = 100000  # Adjust chunk size based on available memory
reader = pd.read_csv("dsf.csv.gz", compression="gzip", low_memory=False, chunksize=chunk_size)

# Open the output file for writing
# Open the output file for writing
output_file = "X_technical.csv.gz"

for i, chunk in enumerate(reader):
    print(f"Processing chunk {i + 1}...")

    # Select only the required columns
    chunk = chunk[columns_to_keep]

    # Standardize column names
    chunk.columns = chunk.columns.str.strip().str.lower()

    # Sort values by permno and date
    chunk = chunk.sort_values(["permno", "date"])

    # Ensure numeric columns are properly formatted
    chunk["prc"] = chunk["prc"].abs()
    chunk["ret"] = pd.to_numeric(chunk["ret"], errors="coerce").fillna(0)

    # Append the processed chunk to the output file
    chunk.to_csv(output_file, index=False, header=(i == 0), mode="a", compression="gzip")  # Write header only for the first chunk

    print(f"Chunk {i + 1} saved.")

print("Finished processing X_technical.")
