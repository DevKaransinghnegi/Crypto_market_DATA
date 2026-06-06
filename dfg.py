import requests
import pandas as pd
from datetime import datetime, timezone

# === Function to convert datetime string → milliseconds ===
def to_milliseconds(dt_str):
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

# === Function to fetch long/short accounts ratio ===
def get_long_short_accounts(symbol, interval, start_time, end_time):
    url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
    params = {
        "symbol": symbol,
        "period": interval,
        "limit": 500,
        "startTime": start_time,
        "endTime": end_time
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not data or "code" in data:  # if error
        print("⚠️ No data found or invalid request:", data)
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["longAccount"] = df["longAccount"].astype(float)
    df["shortAccount"] = df["shortAccount"].astype(float)

    # Add trend column → 1 = Bullish, 0 = Bearish
    df["trend"] = df.apply(lambda row: 1 if row["longAccount"] > row["shortAccount"] else 0, axis=1)

    return df[["timestamp", "longAccount", "shortAccount", "trend"]]

# === User Input ===
symbol = input("Enter Futures pair (example: BTCUSDT, PEPEUSDT, 1000PEPEUSDT): ").upper()
interval = input("Enter timeframe (options: 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d): ")
start_date = input("Enter start date (YYYY-MM-DD HH:MM:SS in UTC): ")
end_date = input("Enter end date (YYYY-MM-DD HH:MM:SS in UTC): ")

start_time = to_milliseconds(start_date)
end_time = to_milliseconds(end_date)

# === Run & Save ===
df = get_long_short_accounts(symbol, interval, start_time, end_time)

if df.empty:
    print("⚠️ No data found. Try adjusting symbol, interval, or date range.")
else:
    output_csv = f"{symbol}_{interval}_long_short_accounts.csv"
    df.to_csv(output_csv, index=False)
    print(f"✅ Data saved to {output_csv}")
    print(df.head())
