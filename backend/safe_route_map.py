import requests
import pandas as pd
import folium
import joblib

from terrain import get_terrain


# ==========================================
# SafePath AI - Risk Colored Route Map
# ==========================================

# Start and destination
start_lat = 12.35
start_lon = 75.75

end_lat = 12.4244
end_lon = 75.7382


# ==========================================
# Load ML model
# ==========================================

model = joblib.load("ml/landslide_model.pkl")


# ==========================================
# Get weather
# ==========================================

weather = pd.read_csv("data/weather.csv")
latest = weather.iloc[0]

rainfall = float(latest["rainfall"])
humidity = float(latest["humidity"])
temperature = float(latest["temperature"])


# ==========================================
# Get road route from OSRM
# ==========================================

url = (
    "https://router.project-osrm.org/route/v1/driving/"
    f"{start_lon},{start_lat};"
    f"{end_lon},{end_lat}"
    "?overview=full&geometries=geojson"
)

response = requests.get(url)

if response.status_code != 200:
    print("Routing service failed.")
    exit()

result = response.json()

if result["code"] != "Ok":
    print("No route found.")
    exit()

route = result["routes"][0]

coordinates = route["geometry"]["coordinates"]


# ==========================================
# Create map
# ==========================================

risk_map = folium.Map(
    location=[start_lat, start_lon],
    zoom_start=12,
    tiles="CartoDB positron"
)


# ==========================================
# Start marker
# ==========================================

folium.Marker(
    [start_lat, start_lon],
    popup="START",
    tooltip="Starting Point",
    icon=folium.Icon(color="green")
).add_to(risk_map)


# ==========================================
# Destination marker
# ==========================================

folium.Marker(
    [end_lat, end_lon],
    popup="DESTINATION",
    tooltip="Destination",
    icon=folium.Icon(color="red")
).add_to(risk_map)


# ==========================================
# Analyze route sections
# ==========================================

risk_values = []

# Analyze every 10th point
sampled_points = coordinates[::10]

for i in range(len(sampled_points) - 1):

    point = sampled_points[i]

    longitude = point[0]
    latitude = point[1]

    # Get terrain
    elevation, slope = get_terrain(
        latitude,
        longitude
    )

    if elevation is None:
        continue

    # ML input
    input_data = [[
        rainfall,
        humidity,
        temperature,
        elevation,
        slope
    ]]

    probability = model.predict_proba(
        input_data
    )[0][1]

    risk = probability * 100

    risk_values.append(risk)


    # ======================================
    # Risk color
    # ======================================

    if risk <= 30:
        color = "green"
        risk_level = "LOW"

    elif risk <= 60:
        color = "orange"
        risk_level = "MEDIUM"

    else:
        color = "red"
        risk_level = "HIGH"


    # Next point
    next_point = sampled_points[i + 1]

    next_lat = next_point[1]
    next_lon = next_point[0]


    # ======================================
    # Popup
    # ======================================

    popup = f"""
    <b>SafePath AI</b><br><br>

    <b>Risk:</b> {risk_level}<br>
    <b>Risk Score:</b> {risk:.2f}%<br><br>

    <b>Rainfall:</b> {rainfall:.2f} mm<br>
    <b>Humidity:</b> {humidity:.2f}%<br>
    <b>Temperature:</b> {temperature:.2f} °C<br>

    <b>Elevation:</b> {elevation:.2f} m<br>
    <b>Slope:</b> {slope:.2f}°
    """


    # ======================================
    # Draw colored route segment
    # ======================================

    folium.PolyLine(
        locations=[
            [latitude, longitude],
            [next_lat, next_lon]
        ],
        color=color,
        weight=7,
        opacity=0.9,
        popup=folium.Popup(
            popup,
            max_width=300
        ),
        tooltip=f"{risk_level} Risk - {risk:.2f}%"
    ).add_to(risk_map)


# ==========================================
# Save map
# ==========================================

risk_map.save(
    "backend/safepath_safe_route.html"
)


# ==========================================
# Print results
# ==========================================

print("======================================")
print("SafePath AI Risk Route Map Created!")
print("======================================")

if risk_values:

    average_risk = sum(risk_values) / len(risk_values)
    maximum_risk = max(risk_values)

    print(
        "Average Risk:",
        round(average_risk, 2),
        "%"
    )

    print(
        "Maximum Risk:",
        round(maximum_risk, 2),
        "%"
    )

print()
print("Map:")
print("backend/safepath_safe_route.html")
