import rasterio
import numpy as np

DEM_FILE = "data/terrain/kodagu_dem.tif"
SLOPE_FILE = "data/terrain/kodagu_slope.tif"

# Example route points
route_points = [
    (12.3375, 75.8069),
    (12.36, 75.79),
    (12.39, 75.77),
    (12.4244, 75.7382)
]

with rasterio.open(DEM_FILE) as dem:
    elevation_data = dem.read(1)

    print("===== Route Terrain Analysis =====")

    for latitude, longitude in route_points:

        # Convert GPS coordinates to raster row/column
        row, col = dem.index(longitude, latitude)

        # Make sure point is inside raster
        if (
            0 <= row < dem.height
            and 0 <= col < dem.width
        ):
            elevation = float(elevation_data[row, col])

            print(
                f"Location: {latitude:.4f}, {longitude:.4f}"
            )
            print(
                f"Elevation: {elevation:.2f} m"
            )
            print()

        else:
            print(
                f"Location {latitude}, {longitude} "
                "is outside the DEM."
            )

# Read slope
with rasterio.open(SLOPE_FILE) as slope:
    slope_data = slope.read(1)

    print("===== Route Slope Analysis =====")

    for latitude, longitude in route_points:

        row, col = slope.index(longitude, latitude)

        if (
            0 <= row < slope.height
            and 0 <= col < slope.width
        ):
            slope_value = float(slope_data[row, col])

            print(
                f"Location: {latitude:.4f}, {longitude:.4f}"
            )
            print(
                f"Slope: {slope_value:.2f} degrees"
            )
            print()