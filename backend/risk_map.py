import folium
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath("."))

from ml.risk_score import calculate_risk_score

# Load dataset
data = pd.read_csv("data/landslide_dataset.csv")

# Create map
risk_map = folium.Map(
    location=[12.35, 75.75],
    zoom_start=10,
    tiles="CartoDB positron"
)

# Add points
for i, row in data.iterrows():

    latitude = 12.0 + (i % 12) * 0.05
    longitude = 75.5 + (i // 12) * 0.08

    score, risk = calculate_risk_score(
        rainfall=float(row["rainfall"]),
        humidity=float(row["humidity"]),
        slope=float(row["slope"]),
        elevation=float(row["elevation"])
    )

    if risk == "LOW":
        color = "green"
    elif risk == "MEDIUM":
        color = "orange"
    else:
        color = "red"

    popup_text = f"""
    <div style="width:220px">
        <h3>SafePath AI</h3>

        <b>Risk Level:</b> {risk}<br>
        <b>Risk Score:</b> {score}/100<br><br>

        <b>🌧 Rainfall:</b> {float(row['rainfall']):.2f} mm<br>
        <b>💧 Humidity:</b> {float(row['humidity']):.2f}%<br>
        <b>🌡 Temperature:</b> {float(row['temperature']):.2f} °C<br>
        <b>⛰ Elevation:</b> {float(row['elevation']):.2f} m<br>
        <b>📐 Slope:</b> {float(row['slope']):.2f}°
    </div>
    """

    folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(
            popup_text,
            max_width=300
        ),
        tooltip=f"{risk} Risk | Score: {score}"
    ).add_to(risk_map)

# Save
risk_map.save("backend/safepath_map.html")

print("================================")
print("SafePath AI GIS Map Created!")
print("================================")
print("Total locations:", len(data))
print("Map file: backend/safepath_map.html")