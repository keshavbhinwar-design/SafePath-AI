import requests
import folium
import pandas as pd
import joblib
import numpy as np

# -----------------------------------------
# LOAD ML MODEL
# -----------------------------------------

model = joblib.load("ml/landslide_model.pkl")

# -----------------------------------------
# START AND DESTINATION
# -----------------------------------------

start = (12.3375, 75.8069)
destination = (12.4244, 75.7382)

# -----------------------------------------
# GET ROUTE
# -----------------------------------------

url = (
    "https://router.project-osrm.org/route/v1/driving/"
    f"{start[1]},{start[0]};"
    f"{destination[1]},{destination[0]}"
    "?overview=full&geometries=geojson"
)

response = requests.get(url)

if response.status_code != 200:
    print("Routing request failed.")
    exit()

data = response.json()

if data["code"] != "Ok":
    print("No route found.")
    exit()

route = data["routes"][0]

distance = route["distance"] / 1000
duration = route["duration"] / 60

coordinates = route["geometry"]["coordinates"]

route_points = [
    [point[1], point[0]]
    for point in coordinates
]

# -----------------------------------------
# LOAD WEATHER DATA
# -----------------------------------------

weather = pd.read_csv("data/weather.csv")

# Use current/latest weather values
latest = weather.iloc[0]

rainfall = float(latest["rainfall"])
humidity = float(latest["humidity"])
temperature = float(latest["temperature"])

# -----------------------------------------
# DEMO TERRAIN VALUES
# -----------------------------------------
# Later these will come from DEM/GIS data.

elevation = 1100
slope = 30

# -----------------------------------------
# PREDICT RISK
# -----------------------------------------

input_data = pd.DataFrame([{
    "rainfall": rainfall,
    "humidity": humidity,
    "temperature": temperature,
    "elevation": elevation,
    "slope": slope
}])

prediction = model.predict(input_data)[0]
probability = model.predict_proba(input_data)[0][1]

risk_score = probability * 100

# -----------------------------------------
# DETERMINE RISK LEVEL
# -----------------------------------------

if risk_score <= 30:
    risk_level = "LOW"
elif risk_score <= 60:
    risk_level = "MEDIUM"
else:
    risk_level = "HIGH"

# -----------------------------------------
# CREATE MAP
# -----------------------------------------

risk_map = folium.Map(
    location=start,
    zoom_start=11,
    tiles="CartoDB positron"
)

folium.Marker(
    start,
    popup="Starting Point",
    tooltip="START"
).add_to(risk_map)

folium.Marker(
    destination,
    popup="Destination",
    tooltip="DESTINATION"
).add_to(risk_map)

# -----------------------------------------
# DRAW ROUTE
# -----------------------------------------

if risk_level == "LOW":
    color = "green"
elif risk_level == "MEDIUM":
    color = "orange"
else:
    color = "red"

popup = f"""
<div style="width:250px">

<h3>SafePath AI</h3>

<b>Route Risk:</b> {risk_level}<br>
<b>Risk Score:</b> {risk_score:.2f}/100<br><br>

<b>Rainfall:</b> {rainfall:.2f} mm<br>
<b>Humidity:</b> {humidity:.2f}%<br>
<b>Temperature:</b> {temperature:.2f} °C<br>
<b>Elevation:</b> {elevation} m<br>
<b>Slope:</b> {slope}°

</div>
"""

folium.PolyLine(
    route_points,
    color=color,
    weight=7,
    opacity=0.9,
    popup=folium.Popup(
        popup,
        max_width=300
    ),
    tooltip=f"{risk_level} Risk | {risk_score:.2f}/100"
).add_to(risk_map)

# -----------------------------------------
# SAVE
# -----------------------------------------

risk_map.save(
    "backend/safepath_real_risk.html"
)

# -----------------------------------------
# TERMINAL OUTPUT
# -----------------------------------------

print("======================================")
print("      SafePath AI Route Analysis")
print("======================================")

print("Distance:", round(distance, 2), "km")
print("Estimated time:", round(duration, 2), "minutes")

print("\nWeather:")
print("Rainfall:", rainfall, "mm")
print("Humidity:", humidity, "%")
print("Temperature:", temperature, "°C")

print("\nTerrain:")
print("Elevation:", elevation, "m")
print("Slope:", slope, "degrees")

print("\nAI Prediction:")
print("Risk probability:", round(risk_score, 2), "%")
print("Risk level:", risk_level)

print("\nMap:")
print("backend/safepath_real_risk.html")

print("======================================")