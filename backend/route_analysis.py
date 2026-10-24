import requests
import pandas as pd
from terrain import get_terrain
import joblib

# Load ML model
model = joblib.load("ml/landslide_model.pkl")

# Start and destination
start_lat = 12.35
start_lon = 75.75

end_lat = 12.4244
end_lon = 75.7382


# ==============================
# Get Route
# ==============================

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


# ==============================
# Weather
# ==============================

weather = pd.read_csv("data/weather.csv")

latest = weather.iloc[0]

rainfall = float(latest["rainfall"])
humidity = float(latest["humidity"])
temperature = float(latest["temperature"])


# ==============================
# Analyze Route Points
# ==============================

risk_values = []

print("\n===== SafePath AI Route Analysis =====")

# Check every 10th route point
sampled_points = coordinates[::10]

for i, point in enumerate(sampled_points):

    longitude = point[0]
    latitude = point[1]

    elevation, slope = get_terrain(
        latitude,
        longitude
    )

    if elevation is None:
        print(
            f"Point {i + 1}: Outside DEM"
        )
        continue

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

    print(
        f"Point {i + 1}: "
        f"Elevation={elevation:.2f} m, "
        f"Slope={slope:.2f}°, "
        f"Risk={risk:.2f}%"
    )


# ==============================
# Overall Route Risk
# ==============================

if len(risk_values) == 0:

    print("\nNo valid terrain points found.")

else:

    average_risk = sum(risk_values) / len(risk_values)

    maximum_risk = max(risk_values)

    if average_risk <= 30:
        risk_level = "LOW"

    elif average_risk <= 60:
        risk_level = "MEDIUM"

    else:
        risk_level = "HIGH"

    print("\n================================")
    print("Overall Route Risk")
    print("================================")

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

    print(
        "Risk Level:",
        risk_level
    )