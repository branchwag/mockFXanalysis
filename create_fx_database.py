import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

conn = sqlite3.connect("fx_trading.db")


def generate_fx_data(pairs=["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"], days=365):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    all_data = []

    for pair in pairs:
        if pair == "EUR/USD":
            initial_value = 1.08
        elif pair == "GBP/USD":
            initial_value = 1.25
        elif pair == "USD/JPY":
            initial_value = 145.0
        elif pair == "AUD/USD":
            initial_value = 0.65
        else:
            initial_value = 1.0

        values = [initial_value]
        for i in range(1, len(dates)):
            vol = 0.005 if "JPY" not in pair else 0.5
            reversion = 0.05 * (initial_value - values[-1])
            change = np.random.normal(reversion, vol)
            values.append(values[-1] + change)

        df_pair = pd.DataFrame(
            {
                "date": dates,
                "pair": pair,
                "close": values,
                "open": [v * (1 + np.random.normal(0, 0.0005)) for v in values],
                "high": [v * (1 + abs(np.random.normal(0, 0.001))) for v in values],
                "low": [v * (1 - abs(np.random.normal(0, 0.001))) for v in values],
                "volume": np.random.lognormal(mean=15, sigma=1, size=len(dates)),
            }
        )
        all_data.append(df_pair)

    return pd.concat(all_data, ignore_index=True)


fx_data = generate_fx_data()
fx_data.to_sql("fx_rates", conn, if_exists="replace", index=False)

# Create a table for trade data
trades = pd.DataFrame(
    {
        "trade_id": range(1, 101),
        "date": np.random.choice(fx_data["date"], 100),
        "pair": np.random.choice(fx_data["pair"], 100),
        "direction": np.random.choice(["BUY", "SELL"], 100),
        "amount": np.random.uniform(1000000, 10000000, 100),
        "rate": np.random.choice(fx_data["close"], 100),
        "trader": np.random.choice(["Trader1", "Trader2", "Trader3", "Trader4"], 100),
        "pnl": np.random.normal(0, 5000, 100),
    }
)
trades.to_sql("trades", conn, if_exists="replace", index=False)

conn.close()
