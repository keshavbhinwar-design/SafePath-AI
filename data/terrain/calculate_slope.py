import rasterio
import numpy as np

DEM_FILE = "data/terrain/kodagu_dem.tif"
SLOPE_FILE = "data/terrain/kodagu_slope.tif"

# Open DEM
with rasterio.open(DEM_FILE) as src:
    elevation = src.read(1)
    profile = src.profile

# Approximate pixel dimensions in metres
pixel_size_x = 30
pixel_size_y = 30

# Calculate elevation change
dz_dx = np.gradient(elevation, pixel_size_x, axis=1)
dz_dy = np.gradient(elevation, pixel_size_y, axis=0)

# Calculate slope
slope = np.degrees(
    np.arctan(
        np.sqrt(dz_dx**2 + dz_dy**2)
    )
)

# Save slope raster
profile.update(
    dtype="float32",
    count=1
)

with rasterio.open(
    SLOPE_FILE,
    "w",
    **profile
) as dst:
    dst.write(slope.astype("float32"), 1)

print("Slope calculation completed!")
print("File:", SLOPE_FILE)
print("Minimum slope:", round(float(slope.min()), 2), "degrees")
print("Maximum slope:", round(float(slope.max()), 2), "degrees")
print("Average slope:", round(float(slope.mean()), 2), "degrees")