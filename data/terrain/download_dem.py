import numpy as np
import rasterio
from rasterio.transform import from_origin


# ============================================================
# SAFEPATH AI - SYNTHETIC KODAGU TERRAIN GENERATOR
# ============================================================
#
# IMPORTANT:
# This creates DEM terrain for prototype/testing purposes.
# It is NOT real Kodagu elevation data.
#
# The terrain contains:
# - hills
# - ridges
# - valleys
# - elevation variation
# - steep and gentle areas
#
# This allows SafePath AI to demonstrate how different
# routes can receive different landslide-risk levels.
# ============================================================


# ------------------------------------------------------------
# AREA
# ------------------------------------------------------------

width = 300
height = 300

min_lon = 75.70
max_lat = 12.45

pixel_size_lon = (0.15 / width)
pixel_size_lat = (0.15 / height)

transform = from_origin(
    min_lon,
    max_lat,
    pixel_size_lon,
    pixel_size_lat
)


# ------------------------------------------------------------
# COORDINATE GRID
# ------------------------------------------------------------

x = np.linspace(0, 1, width)
y = np.linspace(0, 1, height)

X, Y = np.meshgrid(x, y)


# ------------------------------------------------------------
# BASE ELEVATION
# ------------------------------------------------------------

elevation = np.full(
    (height, width),
    750.0,
    dtype=np.float32
)


# ------------------------------------------------------------
# HILL FUNCTION
# ------------------------------------------------------------

def hill(x0, y0, height_value, width_value):
    return height_value * np.exp(
        -(
            ((X - x0) ** 2) / width_value
            + ((Y - y0) ** 2) / width_value
        )
    )


# ------------------------------------------------------------
# MAJOR HILLS
# ------------------------------------------------------------

elevation += hill(
    0.25,
    0.25,
    650,
    0.025
)

elevation += hill(
    0.70,
    0.25,
    850,
    0.035
)

elevation += hill(
    0.45,
    0.65,
    550,
    0.020
)

elevation += hill(
    0.82,
    0.75,
    700,
    0.030
)

elevation += hill(
    0.18,
    0.75,
    450,
    0.040
)


# ------------------------------------------------------------
# RIDGE
# ------------------------------------------------------------

ridge = (
    250
    * np.exp(-((Y - (0.75 - 0.45 * X)) ** 2) / 0.008)
)

elevation += ridge


# ------------------------------------------------------------
# VALLEY
# ------------------------------------------------------------

valley = (
    250
    * np.exp(
        -(
            ((X - 0.55) ** 2)
            + ((Y - 0.45) ** 2)
        ) / 0.05
    )
)

elevation -= valley


# ------------------------------------------------------------
# SMALL TERRAIN VARIATION
# ------------------------------------------------------------

np.random.seed(42)

noise = np.random.normal(
    0,
    8,
    (height, width)
)

elevation += noise


# ------------------------------------------------------------
# LIMIT ELEVATION
# ------------------------------------------------------------

elevation = np.clip(
    elevation,
    500,
    1800
)


# ------------------------------------------------------------
# SAVE DEM
# ------------------------------------------------------------

profile = {
    "driver": "GTiff",
    "height": height,
    "width": width,
    "count": 1,
    "dtype": "float32",
    "crs": "EPSG:4326",
    "transform": transform,
}


output_file = "data/terrain/kodagu_dem.tif"

with rasterio.open(
    output_file,
    "w",
    **profile
) as dst:

    dst.write(
        elevation.astype(np.float32),
        1
    )


# ------------------------------------------------------------
# INFORMATION
# ------------------------------------------------------------

print()
print("========================================")
print("      SAFEPATH AI TERRAIN SYSTEM")
print("========================================")
print()

print("Synthetic Kodagu DEM created successfully.")

print()
print("Terrain characteristics:")
print("------------------------")
print("Minimum elevation:",
      round(float(elevation.min()), 2), "m")

print("Maximum elevation:",
      round(float(elevation.max()), 2), "m")

print("Average elevation:",
      round(float(elevation.mean()), 2), "m")

print()
print("Grid size:", width, "x", height)

print()
print("Saved to:")
print(output_file)

print()
print("NOTE:")
print("This is synthetic terrain for prototype testing.")
print("It is NOT real Kodagu elevation data.")

print()
print("========================================")