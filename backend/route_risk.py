import requests
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

# Route information
distance = route["distance"] / 1000
duration = route["duration"] / 60

# Get route coordinates
coordinates = route["geometry"]["coordinates"]

print("======================================")
print("       SafePath AI Route Analysis")
print("======================================")

print("Route distance:", round(distance, 2), "km")
print("Estimated time:", round(duration, 2), "minutes")
print("Route points:", len(coordinates))

# ------------------------------------------------
# DEMO RISK CALCULATION
# ------------------------------------------------
# For now we generate synthetic risk values.
# Later these will come from our ML + terrain model.

np.random.seed(42)

risk_values = np.random.uniform(
    20,
    90,
    len(coordinates)
)

average_risk = np.mean(risk_values)
maximum_risk = np.max(risk_values)

print("\nAverage risk:", round(average_risk, 2), "/ 100")
print("Maximum risk:", round(maximum_risk, 2), "/ 100")

# Determine overall route risk
if average_risk <= 30:
    risk_level = "LOW"
elif average_risk <= 60:
    risk_level = "MEDIUM"
else:
    risk_level = "HIGH"

print("\nOverall Route Risk:", risk_level)

if risk_level == "LOW":
    print("Recommendation: ✅ Route appears relatively safer.")
elif risk_level == "MEDIUM":
    print("Recommendation: ⚠️ Use caution.")
else:
    print("Recommendation: 🔴 High predicted risk.")
    print("Consider another route if available.")

print("======================================")