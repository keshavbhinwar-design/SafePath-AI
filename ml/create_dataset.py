import pandas as pd
import numpy as np
import rasterio


# ============================================================
# SAFEPATH AI - DATASET CREATION
# ============================================================

print()
print("========================================")
print("     SAFEPATH AI DATASET CREATION")
print("========================================")
print()


# ============================================================
# FILE PATHS
# ============================================================

WEATHER_FILE = "data/weather.csv"
DEM_FILE = "data/terrain/kodagu_dem.tif"
SLOPE_FILE = "data/terrain/kodagu_slope.tif"

OUTPUT_FILE = "data/landslide_dataset.csv"


# ============================================================
# LOAD WEATHER DATA
# ============================================================

weather = pd.read_csv(WEATHER_FILE)

print("Weather records loaded:", len(weather))


# ============================================================
# LOAD REAL TERRAIN RASTERS
# ============================================================

with rasterio.open(DEM_FILE) as dem:

    dem_data = dem.read(1)

    dem_values = dem_data[
        np.isfinite(dem_data)
    ].flatten()


with rasterio.open(SLOPE_FILE) as slope:

    slope_data = slope.read(1)

    slope_values = slope_data[
        np.isfinite(slope_data)
    ].flatten()


print("DEM values loaded:", len(dem_values))
print("Slope values loaded:", len(slope_values))


# ============================================================
# SAMPLE TERRAIN VALUES
# ============================================================

np.random.seed(42)

weather["elevation"] = np.random.choice(
    dem_values,
    size=len(weather)
)

weather["slope"] = np.random.choice(
    slope_values,
    size=len(weather)
)


# ============================================================
# CLEAN TERRAIN VALUES
# ============================================================

weather["elevation"] = (
    weather["elevation"]
    .clip(0, None)
    .round(2)
)

weather["slope"] = (
    weather["slope"]
    .clip(0, 90)
    .round(2)
)


# ============================================================
# CREATE PROTOTYPE LABEL
# ============================================================

# IMPORTANT:
# These are still synthetic prototype labels.
# They are NOT real historical landslide observations.
#
# The purpose of this stage is to connect the model
# with realistic terrain values while we prepare
# the real historical landslide dataset.

risk_score = (
    weather["rainfall"] * 3
    + weather["slope"] * 2
    + weather["humidity"] * 0.5
)


threshold = risk_score.median()


weather["landslide"] = (
    risk_score >= threshold
).astype(int)


# ============================================================
# SAVE DATASET
# ============================================================

weather.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("Dataset created successfully!")
print()

print("Dataset shape:")
print(weather.shape)

print()

print("Features:")
print([
    "rainfall",
    "rainfall_6h",
    "rainfall_12h",
    "rainfall_24h",
    "humidity",
    "temperature",
    "elevation",
    "slope"
])

print()

print("Landslide labels:")
print(
    weather["landslide"].value_counts()
)

print()

print("Terrain statistics:")

print(
    "Elevation:",
    round(weather["elevation"].min(), 2),
    "to",
    round(weather["elevation"].max(), 2),
    "m"
)

print(
    "Slope:",
    round(weather["slope"].min(), 2),
    "to",
    round(weather["slope"].max(), 2),
    "degrees"
)

print()

print("First 5 rows:")
print(
    weather.head()
)

print()

print("Saved to:")
print(OUTPUT_FILE)

print()
print("========================================")
print(" NOTE: LANDSLIDE LABELS ARE SYNTHETIC   ")
print("       FOR PROTOTYPE DEVELOPMENT ONLY   ")
print("========================================")