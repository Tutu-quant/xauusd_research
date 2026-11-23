
from pathlib import Path
import pandas as pd

# 1. Đọc dữ liệu Bronze
DATA_DIR = Path(
    "data/bronze/market/dukascopy_raw/d1/Forex/Metals/XAU-USD"
)

bid = pd.read_parquet(DATA_DIR / "BID" / "all.parquet")
ask = pd.read_parquet(DATA_DIR / "ASK" / "all.parquet")


# 2. Hàm kiểm tra chất lượng
def check_quality(df, name):
    print(f"\n========== {name} ==========")

    print("Rows:", len(df))
    print("Columns:", list(df.columns))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate timestamps:", df["time"].duplicated().sum())

    # Kiểm tra logic OHLC
    invalid_ohlc = (
        (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["low"] > df["open"])
        | (df["low"] > df["close"])
        | (df["high"] < df["low"])
    )

    print("Invalid OHLC rows:", invalid_ohlc.sum())

    print("\nDate range:")
    print(df["time"].min(), "->", df["time"].max())


# 3. Kiểm tra riêng BID và ASK
check_quality(bid, "BID")
check_quality(ask, "ASK")


# 4. Kiểm tra sự đồng bộ timestamp
bid_times = set(bid["time"])
ask_times = set(ask["time"])

print("\n========== BID vs ASK ==========")
print("Common timestamps:", len(bid_times & ask_times))
print("Only BID:", len(bid_times - ask_times))
print("Only ASK:", len(ask_times - bid_times))


# 5. Kiểm tra giá trị OHLC có dương không
print("\n========== PRICE VALIDATION ==========")

for name, df in [("BID", bid), ("ASK", ask)]:
    price_columns = ["open", "high", "low", "close"]
    invalid_prices = (df[price_columns] <= 0).any(axis=1).sum()

    print(f"{name} non-positive price rows:", invalid_prices)
# 6. Kiểm tra các ngày không có dữ liệu
print("\n========== DATE GAP ANALYSIS ==========")

# Chuyển timestamp về ngày UTC để kiểm tra
bid_dates = pd.DatetimeIndex(
    bid["time"].dt.normalize().unique()
).sort_values()

ask_dates = pd.DatetimeIndex(
    ask["time"].dt.normalize().unique()
).sort_values()

# Kiểm tra các ngày trong tuần từ thứ Hai đến thứ Sáu
# Đây chỉ là phép kiểm tra sơ bộ, chưa phải lịch giao dịch vàng chính thức
expected_weekdays = pd.date_range(
    start="2020-01-01",
    end="2020-12-31",
    freq="B",
    tz="UTC"
)

missing_weekdays = expected_weekdays.difference(bid_dates)

print("Unique BID dates:", len(bid_dates))
print("Unique ASK dates:", len(ask_dates))
print("Missing weekdays (UTC):", len(missing_weekdays))

print("\nFirst 30 missing weekdays:")
print(missing_weekdays[:30])

# Kiểm tra khoảng cách giữa hai bản ghi liên tiếp
gaps = bid_dates.to_series().diff().dropna()

print("\nLargest date gaps:")
print(gaps.sort_values(ascending=False).head(10))

# Thống kê số bản ghi theo tháng
monthly_counts = (
    bid.assign(month=bid["time"].dt.strftime("%Y-%m"))
    .groupby("month")
    .size()
)

print("\nMonthly row counts:")
print(monthly_counts)
