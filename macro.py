import os
import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

# Load environment variables
load_dotenv()

# Get FRED API key
api_key = os.getenv("FRED_API_KEY")

if not api_key:
    raise ValueError("FRED_API_KEY was not found in .env")

# Connect to FRED
fred = Fred(api_key=api_key)

# Get macroeconomic indicators
gdp = fred.get_series("GDP")
cpi = fred.get_series("CPIAUCSL")
unemployment = fred.get_series("UNRATE")

# Combine into one DataFrame
macro_data = pd.concat(
    [gdp, cpi, unemployment],
    axis=1
)

macro_data.columns = [
    "GDP",
    "CPI",
    "UNRATE"
]

# Save the data
macro_data.to_csv("data/raw_macro.csv")

print("Macro data downloaded successfully!")
print("\nShape:", macro_data.shape)
print("\nLatest values:")
print(macro_data.tail())

print("\nSaved to: data/raw_macro.csv")