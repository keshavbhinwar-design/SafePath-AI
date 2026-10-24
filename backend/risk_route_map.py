import requests
import folium
import numpy as np

# Start and destination
start = (12.3375, 75.8069)
destination = (12.4244, 75.7382)

# Get route from OSRM
url = (
    "https://router.project-osrm.org/route/v1/driving/"
    f"{start[1]},{start[0]};"
    f"{destination[1]},{destination[0]}"
    "?overview=full&geometries=geojson"
)

response = requests.get(url)

if response.status_code != 200:
    print("Could not get route.")
    exit()

data = response.json()

if data["code"] != "Ok":
    print("No route found.")
    exit()

route = data["routes"][0]

distance = route["distance"] / 1000
duration = route["duration"] / 60

# Route coordinates
coordinates = route["geometry"]["coordinates"]

# Convert coordinates
route_points = [
    [point[1], point[0]]
    for point in coordinates
]

# -----------------------------------------
# DEMO RISK VALUES
# -----------------------------------------

np.random.seed(42)

risk_values = np.random.uniform(
    10,
    90,
    len(route_points)
)

# -----------------------------------------
# CREATE MAP
# -----------------------------------------

risk_map = folium.Map(
    location=start,
    zoom_start=11,
    tiles="CartoDB positron"
)

# Start marker
folium.Marker(
    start,
    popup="Starting Point",
    tooltip="START"
).add_to(risk_map)

# Destination marker
folium.Marker(
    destination,
    popup="Destination",
    tooltip="DESTINATION"
).add_to(risk_map)

# -----------------------------------------
# DRAW COLORED ROUTE
# -----------------------------------------

for i in range(len(route_points) - 1):

    risk = risk_values[i]

    if risk <= 30:
        color = "green"
        level = "LOW"

    elif risk <= 60:
        color = "orange"
        level = "MEDIUM"

    else:
        color = "red"
        level = "HIGH"

    popup = f"""
    <b>SafePath AI</b><br>
    Risk Level: {level}<br>
    Risk Score: {risk:.2f}/100
    """

    folium.PolyLine(
        [
            route_points[i],
            route_points[i + 1]
        ],
        color=color,
        weight=7,
        opacity=0.9,
        popup=popup
    ).add_to(risk_map)

# -----------------------------------------
# SAVE MAP
# -----------------------------------------

risk_map.save(
    "backend/safepath_risk_route.html"
)

print("======================================")
print(" SafePath AI Risk Route Map Created!")
print("======================================")
print("Distance:", round(distance, 2), "km")
print("Time:", round(duration, 2), "minutes")
print("Map: backend/safepath_risk_route.html")