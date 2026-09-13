import os
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()

api_key = os.getenv("FRED_API_KEY")

if not api_key:
    raise ValueError("FRED_API_KEY was not found in .env")

fred = Fred(api_key=api_key)

gdp = fred.get_series("GDP")

print("FRED connection successful!")
print("\nLatest GDP values:")
print(gdp.tail())