import requests
import folium

# Start and destination
start = (12.3375, 75.8069)
destination = (12.4244, 75.7382)

# OSRM requires longitude,latitude
url = (
    "https://router.project-osrm.org/route/v1/driving/"
    f"{start[1]},{start[0]};"
    f"{destination[1]},{destination[0]}"
    "?overview=full&geometries=geojson"
)

response = requests.get(url)

if response.status_code == 200:

    data = response.json()

    if data["code"] == "Ok":

        route = data["routes"][0]

        distance = route["distance"] / 1000
        duration = route["duration"] / 60

        # Extract route coordinates
        coordinates = route["geometry"]["coordinates"]

        # Convert [longitude, latitude] → [latitude, longitude]
        route_points = [
            [point[1], point[0]]
            for point in coordinates
        ]

        # Create map
        route_map = folium.Map(
            location=start,
            zoom_start=11,
            tiles="CartoDB positron"
        )

        # Start marker
        folium.Marker(
            start,
            popup="Starting Point",
            tooltip="Start"
        ).add_to(route_map)

        # Destination marker
        folium.Marker(
            destination,
            popup="Destination",
            tooltip="Destination"
        ).add_to(route_map)

        # Draw route
        folium.PolyLine(
            route_points,
            weight=6,
            opacity=0.8,
            tooltip=f"Route: {distance:.2f} km"
        ).add_to(route_map)

        # Save map
        route_map.save(
            "backend/safepath_route.html"
        )

        print("================================")
        print("SafePath AI Route Created!")
        print("================================")
        print("Distance:", round(distance, 2), "km")
        print("Estimated time:", round(duration, 2), "minutes")
        print("Map: backend/safepath_route.html")

    else:
        print("No route found.")

else:
    print("Routing request failed.")
    print("Status:", response.status_code)