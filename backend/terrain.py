import rasterio


DEM_FILE = "data/terrain/kodagu_dem.tif"
SLOPE_FILE = "data/terrain/kodagu_slope.tif"


def get_terrain(latitude, longitude):

    with rasterio.open(DEM_FILE) as dem:

        row, col = dem.index(longitude, latitude)

        if (
            row < 0
            or row >= dem.height
            or col < 0
            or col >= dem.width
        ):
            return None, None

        elevation = float(
            dem.read(1)[row, col]
        )

    with rasterio.open(SLOPE_FILE) as slope:

        row, col = slope.index(
            longitude,
            latitude
        )

        slope_value = float(
            slope.read(1)[row, col]
        )

    return elevation, slope_value