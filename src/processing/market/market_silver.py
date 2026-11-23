from pathlib import Path
import pandas as pd

BRONZE_DIR = Path(
    "data/bronze/market/dukascopy_raw/d1/Forex/Metals/XAU-USD"
)

SILVER_DIR = Path("data/silver/market")

SILVER_DIR.mkdir(parents=True, exist_ok=True)

# BID data and ASK data
bid = pd.read_parquet(BRONZE_DIR / "BID" / "all.parquet")
ask = pd.read_parquet(BRONZE_DIR / "ASK" / "all.parquet")

print("BID data shape:", bid.shape)
print("ASK data shape:", ask.shape)

print("\nBID preview:")
print(bid.head())
print("\nASK preview:")
print(ask.head())

# Đổi tên cột BID
bid = bid.rename(columns={
    "open": "bid_open",
    "high": "bid_high",
    "low": "bid_low",
    "close": "bid_close",
    "volume": "bid_volume"
})

# Đổi tên cột ASK
ask = ask.rename(columns={
    "open": "ask_open",
    "high": "ask_high",
    "low": "ask_low",
    "close": "ask_close",
    "volume": "ask_volume"
})

#merge BID và ASK theo timestamp
market = pd.merge(
    bid,
    ask,
    on="time",
    how="inner",
    validate="one_to_one"
)

print("\nMerged market shape:", market.shape)
print("\nMerged market preview:")
print(market.head())

# Tính spread tại giá đóng cửa
market["spread_close"] = (
    market["ask_close"] - market["bid_close"]
)

print("\nSpread preview:")
print(market[["time", "bid_close", "ask_close", "spread_close"]].head())

print("\n========== SILVER QUALITY CHECK ==========")

print("Rows:", len(market))
print("Columns:", len(market.columns))

print("\nMissing values:")
print(market.isnull().sum())

print("\nDuplicate timestamps:", market["time"].duplicated().sum())

print("\nNegative spread rows:",
      (market["spread_close"] < 0).sum())

print("\nTimestamp sorted:",
      market["time"].is_monotonic_increasing)

# Lưu dữ liệu Silver
parquet_path = SILVER_DIR / "XAUUSD_D1_2020_2025.parquet"
csv_path = SILVER_DIR / "XAUUSD_D1_2020_2025.csv"

market.to_parquet(parquet_path, index=False)
market.to_csv(csv_path, index=False)

print("\n========== EXPORT COMPLETED ==========")
print("Parquet:", parquet_path)
print("CSV:", csv_path)

# ==========================================
# VERIFY EXPORTED FILES
# ==========================================

print("\n========== VERIFY EXPORTED FILES ==========")

# Đọc lại Parquet
parquet_check = pd.read_parquet(parquet_path)

print("\nParquet shape:", parquet_check.shape)
print("\nParquet dtypes:")
print(parquet_check.dtypes)

print("\nParquet time range:")
print(parquet_check["time"].min())
print(parquet_check["time"].max())

# Đọc lại CSV
csv_check = pd.read_csv(csv_path, parse_dates=["time"])

print("\nCSV shape:", csv_check.shape)
print("\nCSV time dtype:")
print(csv_check["time"].dtype)

# So sánh dữ liệu
print("\nParquet equals original:",
      market.equals(parquet_check))

print("CSV rows:", len(csv_check))
print("CSV columns:", len(csv_check.columns))