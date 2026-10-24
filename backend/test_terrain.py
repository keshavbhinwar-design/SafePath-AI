from terrain import get_terrain


latitude = 12.35
longitude = 75.75


elevation, slope = get_terrain(
    latitude,
    longitude
)


if elevation is not None:

    print("===== Terrain Test =====")
    print("Latitude:", latitude)
    print("Longitude:", longitude)
    print("Elevation:", round(elevation, 2), "m")
    print("Slope:", round(slope, 2), "degrees")

else:

    print("Location is outside the DEM.")