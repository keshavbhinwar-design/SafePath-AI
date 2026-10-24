import requests
import pandas as pd


# =========================================================
# KODAGU STUDY AREA
# =========================================================

latitude = 12.35
longitude = 75.75


# =========================================================
# OPEN-METEO API
# =========================================================

url = "https://api.open-meteo.com/v1/forecast"


params = {

    "latitude": latitude,

    "longitude": longitude,

    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "rain",
        "precipitation"
    ],

    "forecast_days": 3,

    "timezone": "Asia/Kolkata"

}


# =========================================================
# REQUEST WEATHER DATA
# =========================================================

response = requests.get(
    url,
    params=params,
    timeout=20
)


response.raise_for_status()


data = response.json()


# =========================================================
# CREATE DATAFRAME
# =========================================================

hourly = data["hourly"]


weather = pd.DataFrame({

    "time":
        hourly["time"],

    "temperature":
        hourly["temperature_2m"],

    "humidity":
        hourly["relative_humidity_2m"],

    "rainfall":
        hourly["rain"],

    "precipitation":
        hourly["precipitation"]

})


# =========================================================
# RAINFALL ACCUMULATION
# =========================================================

# Rainfall during previous 6 hours.

weather["rainfall_6h"] = (
    weather["rainfall"]
    .rolling(
        window=6,
        min_periods=1
    )
    .sum()
)


# Rainfall during previous 12 hours.

weather["rainfall_12h"] = (
    weather["rainfall"]
    .rolling(
        window=12,
        min_periods=1
    )
    .sum()
)


# Rainfall during previous 24 hours.

weather["rainfall_24h"] = (
    weather["rainfall"]
    .rolling(
        window=24,
        min_periods=1
    )
    .sum()
)


# =========================================================
# ROUND VALUES
# =========================================================

weather["temperature"] = weather[
    "temperature"
].round(2)


weather["humidity"] = weather[
    "humidity"
].round(2)


weather["rainfall"] = weather[
    "rainfall"
].round(2)


weather["precipitation"] = weather[
    "precipitation"
].round(2)


weather["rainfall_6h"] = weather[
    "rainfall_6h"
].round(2)


weather["rainfall_12h"] = weather[
    "rainfall_12h"
].round(2)


weather["rainfall_24h"] = weather[
    "rainfall_24h"
].round(2)


# =========================================================
# SAVE WEATHER DATA
# =========================================================

weather.to_csv(
    "data/weather.csv",
    index=False
)


# =========================================================
# DISPLAY CURRENT DATA
# =========================================================

print()
print("========================================")
print("       SAFEPATH AI WEATHER SYSTEM")
print("========================================")

print()

print(
    "Location:",
    data.get("latitude"),
    data.get("longitude")
)

print()

print(
    "Weather data downloaded successfully."
)

print(
    "Total hourly records:",
    len(weather)
)

print()

print("Latest weather:")

print(
    weather.iloc[0].to_string()
)

print()

print("Rainfall accumulation:")

print(
    "6 hour :",
    weather.iloc[0]["rainfall_6h"],
    "mm"
)

print(
    "12 hour:",
    weather.iloc[0]["rainfall_12h"],
    "mm"
)

print(
    "24 hour:",
    weather.iloc[0]["rainfall_24h"],
    "mm"
)

print()

print("Saved to:")
print("data/weather.csv")

print()
print("========================================")