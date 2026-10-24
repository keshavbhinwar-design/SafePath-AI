import folium
import pandas as pd
from folium.plugins import HeatMap

# Load dataset
data = pd.read_csv("data/landslide_dataset.csv")

# Create map
risk_map = folium.Map(
    location=[12.35, 75.75],
    zoom_start=10,
    tiles="CartoDB positron"
)

# Create heatmap points
heat_data = []

for i, row in data.iterrows():

    latitude = 12.0 + (i % 12) * 0.05
    longitude = 75.5 + (i // 12) * 0.08

    # Calculate risk intensity
    risk_value = (
        row["rainfall"] * 3
        + row["slope"] * 2
        + row["humidity"] * 0.5
    )

    heat_data.append([
        latitude,
        longitude,
        risk_value
    ])

# Add heatmap
HeatMap(
    heat_data,
    radius=25,
    blur=20,
    min_opacity=0.4
).add_to(risk_map)

# Save map
risk_map.save("backend/risk_zones.html")

print("================================")
print("SafePath AI Risk Zone Map Created!")
print("================================")
print("Map file: backend/risk_zones.html")