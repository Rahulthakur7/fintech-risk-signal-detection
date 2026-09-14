import pandas as pd
from sqlalchemy import create_engine

# MySQL connection
engine = create_engine(
    "mysql+mysqlconnector://risk_user:RiskProject%4012345@127.0.0.1:3306/fintech_risk"
)


# Load stock prices


prices = pd.read_csv("data/raw_prices.csv")

# Convert from wide format to long format
prices = prices.melt(
    id_vars=["Date"],
    var_name="ticker",
    value_name="close_price"
)

# Clean columns
prices["Date"] = pd.to_datetime(prices["Date"]).dt.date
prices = prices.dropna(subset=["close_price"])

# Loading into MySQL
prices.to_sql(
    "daily_prices",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Stock prices loaded successfully!")
print("Rows loaded:", len(prices))



# Load macro indicators


macro = pd.read_csv("data/raw_macro.csv")

macro["Unnamed: 0"] = pd.to_datetime(macro["Unnamed: 0"]).dt.date

macro = macro.rename(
    columns={"Unnamed: 0": "date"}
)

# Remove rows where all indicators are missing
macro = macro.dropna(
    subset=["GDP", "CPI", "UNRATE"],
    how="all"
)

macro.to_sql(
    "macro_indicators",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Macro data loaded successfully!")
print("Rows loaded:", len(macro))

print("\nData loading complete!")