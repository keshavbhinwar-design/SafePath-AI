import requests
import pandas as pd
import numpy as np

from backend.terrain import get_terrain
from ml.risk_score import calculate_risk_score


# =========================================================
# RISK CLASSIFICATION
# =========================================================

def classify_risk(score):

    if score < 25:
        return "LOW"

    elif score < 50:
        return "MEDIUM"

    elif score < 75:
        return "HIGH"

    else:
        return "VERY HIGH"


# =========================================================
# RAINFALL RISK
# =========================================================

def calculate_rainfall_risk(
    rainfall,
    rainfall_6h,
    rainfall_12h,
    rainfall_24h
):

    risk = 0

    # Current rainfall
    if rainfall >= 5:
        risk += 10

    if rainfall >= 15:
        risk += 15

    if rainfall >= 25:
        risk += 20

    if rainfall >= 40:
        risk += 15

    # 6-hour rainfall
    if rainfall_6h >= 25:
        risk += 10

    if rainfall_6h >= 50:
        risk += 15

    if rainfall_6h >= 75:
        risk += 15

    # 12-hour rainfall
    if rainfall_12h >= 50:
        risk += 10

    if rainfall_12h >= 100:
        risk += 15

    # 24-hour rainfall
    if rainfall_24h >= 75:
        risk += 10

    if rainfall_24h >= 100:
        risk += 15

    if rainfall_24h >= 150:
        risk += 20

    return min(risk, 100)


# =========================================================
# SLOPE RISK
# =========================================================

def calculate_slope_risk(slope):

    if slope < 10:
        return 5

    elif slope < 20:
        return 20

    elif slope < 30:
        return 45

    elif slope < 40:
        return 70

    else:
        return 90


# =========================================================
# ELEVATION RISK
# =========================================================

def calculate_elevation_risk(elevation):

    if elevation is None:
        return 30

    if elevation < 500:
        return 10

    elif elevation < 1000:
        return 20

    elif elevation < 1500:
        return 35

    elif elevation < 2000:
        return 45

    else:
        return 55


# =========================================================
# HUMIDITY RISK
# =========================================================

def calculate_humidity_risk(humidity):

    if humidity < 60:
        return 5

    elif humidity < 75:
        return 15

    elif humidity < 85:
        return 30

    elif humidity < 95:
        return 55

    else:
        return 75


# =========================================================
# WEATHER + TERRAIN INTERACTION
# =========================================================

def calculate_interaction_risk(
    rainfall,
    rainfall_6h,
    rainfall_24h,
    slope
):

    risk = 0

    # Heavy rain + steep slope
    if rainfall >= 25 and slope >= 25:
        risk += 20

    # Heavy 6-hour rainfall + steep slope
    if rainfall_6h >= 50 and slope >= 25:
        risk += 20

    # Heavy 24-hour rainfall + steep slope
    if rainfall_24h >= 100 and slope >= 30:
        risk += 25

    # Extreme rainfall
    if rainfall_24h >= 150:
        risk += 20

    return min(risk, 100)


# =========================================================
# SEGMENT RISK
# =========================================================

def calculate_segment_risk(
    rainfall,
    rainfall_6h,
    rainfall_12h,
    rainfall_24h,
    humidity,
    temperature,
    elevation,
    slope
):

    # -----------------------------------------------------
    # EXISTING SYNTHETIC RISK MODEL
    # -----------------------------------------------------

    ml_score, ml_level = calculate_risk_score(
        rainfall=rainfall,
        humidity=humidity,
        slope=slope,
        elevation=elevation
    )

    ml_risk = float(ml_score)


    # -----------------------------------------------------
    # ADDITIONAL RISK COMPONENTS
    # -----------------------------------------------------

    slope_risk = calculate_slope_risk(
        slope
    )

    elevation_risk = calculate_elevation_risk(
        elevation
    )

    rainfall_risk = calculate_rainfall_risk(
        rainfall,
        rainfall_6h,
        rainfall_12h,
        rainfall_24h
    )

    humidity_risk = calculate_humidity_risk(
        humidity
    )

    interaction_risk = calculate_interaction_risk(
        rainfall,
        rainfall_6h,
        rainfall_24h,
        slope
    )


    # -----------------------------------------------------
    # COMBINED RISK
    # -----------------------------------------------------

    risk = (

        ml_risk * 0.20

        + slope_risk * 0.30

        + elevation_risk * 0.05

        + rainfall_risk * 0.25

        + humidity_risk * 0.05

        + interaction_risk * 0.15

    )


    # -----------------------------------------------------
    # EXTRA SENSITIVITY PENALTIES
    # -----------------------------------------------------

    if rainfall >= 25 and slope >= 25:
        risk += 8


    if rainfall_6h >= 50 and slope >= 25:
        risk += 8


    if rainfall_24h >= 100 and slope >= 30:
        risk += 12


    if rainfall_24h >= 150:
        risk += 8


    risk = min(
        max(risk, 0),
        100
    )


    return {

        "risk": round(
            risk,
            2
        ),

        "level": classify_risk(
            risk
        ),

        "ml_risk": round(
            ml_risk,
            2
        ),

        "slope_risk": round(
            slope_risk,
            2
        ),

        "elevation_risk": round(
            elevation_risk,
            2
        ),

        "rainfall_risk": round(
            rainfall_risk,
            2
        ),

        "humidity_risk": round(
            humidity_risk,
            2
        ),

        "interaction_risk": round(
            interaction_risk,
            2
        )

    }


# =========================================================
# GET ROUTE FROM OSRM
# =========================================================

def get_osrm_route(
    start_lat,
    start_lon,
    end_lat,
    end_lon
):

    url = (
        "https://router.project-osrm.org/"
        "route/v1/driving/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
        "?overview=full&geometries=geojson"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if data.get("code") != "Ok":
            return None

        return data["routes"][0]

    except Exception as error:

        print(
            "OSRM routing error:",
            error
        )

        return None


# =========================================================
# CREATE ROUTE SEGMENTS
# =========================================================

def create_segments(
    geometry,
    rainfall,
    rainfall_6h,
    rainfall_12h,
    rainfall_24h,
    humidity,
    temperature
):

    coordinates = geometry["coordinates"]

    segments = []

    for i in range(
        len(coordinates) - 1
    ):

        lon1, lat1 = coordinates[i]

        lon2, lat2 = coordinates[i + 1]


        elevation, slope = get_terrain(
            lat1,
            lon1
        )


        # Fallback values
        if elevation is None:
            elevation = 1000

        if slope is None:
            slope = 15


        result = calculate_segment_risk(

            rainfall,
            rainfall_6h,
            rainfall_12h,
            rainfall_24h,

            humidity,
            temperature,

            elevation,
            slope

        )


        segments.append({

            "segment_id": i + 1,

            "start": {
                "lat": round(
                    lat1,
                    6
                ),
                "lon": round(
                    lon1,
                    6
                )
            },

            "end": {
                "lat": round(
                    lat2,
                    6
                ),
                "lon": round(
                    lon2,
                    6
                )
            },

            "risk": result["risk"],

            "level": result["level"],

            "elevation": round(
                elevation,
                2
            ),

            "slope": round(
                slope,
                2
            ),

            "ml_risk": result[
                "ml_risk"
            ],

            "rainfall_risk": result[
                "rainfall_risk"
            ],

            "interaction_risk": result[
                "interaction_risk"
            ]

        })


    return segments


# =========================================================
# ROUTE SUMMARY
# =========================================================

def summarize_route(
    segments,
    distance_km,
    duration_min
):

    if not segments:
        return None


    risks = [
        segment["risk"]
        for segment in segments
    ]


    average_risk = np.mean(
        risks
    )

    maximum_risk = np.max(
        risks
    )


    low = sum(
        1
        for segment in segments
        if segment["level"] == "LOW"
    )

    medium = sum(
        1
        for segment in segments
        if segment["level"] == "MEDIUM"
    )

    high = sum(
        1
        for segment in segments
        if segment["level"] == "HIGH"
    )

    very_high = sum(
        1
        for segment in segments
        if segment["level"] == "VERY HIGH"
    )


    dangerous_segments = (
        high + very_high
    )


    dangerous_percentage = (
        dangerous_segments
        / len(segments)
        * 100
    )


    # -----------------------------------------------------
    # SAFETY SCORE
    # -----------------------------------------------------

    safety_score = (

        (100 - average_risk) * 0.40

        + (100 - maximum_risk) * 0.25

        + (100 - dangerous_percentage) * 0.35

    )


    safety_score = max(
        0,
        min(
            safety_score,
            100
        )
    )


    return {

        "distance_km": round(
            distance_km,
            2
        ),

        "duration_min": round(
            duration_min,
            2
        ),

        "average_risk": round(
            average_risk,
            2
        ),

        "maximum_risk": round(
            maximum_risk,
            2
        ),

        "risk_level": classify_risk(
            average_risk
        ),

        "safety_score": round(
            safety_score,
            2
        ),

        "dangerous_segment_percentage":
            round(
                dangerous_percentage,
                2
            ),

        "segment_summary": {

            "total": len(
                segments
            ),

            "low": low,

            "medium": medium,

            "high": high,

            "very_high": very_high

        },

        "segments": segments

    }


# =========================================================
# MAIN ROUTE ANALYSIS
# =========================================================

def analyze_route_options(

    start_lat,
    start_lon,

    end_lat,
    end_lon,

    rainfall=None,
    rainfall_6h=None,
    rainfall_12h=None,
    rainfall_24h=None,

    humidity=None,
    temperature=None

):

    # -----------------------------------------------------
    # LOAD WEATHER DATA
    # -----------------------------------------------------

    weather = pd.read_csv(
        "data/weather.csv"
    )

    latest = weather.iloc[0]


    if rainfall is None:

        rainfall = float(
            latest["rainfall"]
        )


    if rainfall_6h is None:

        rainfall_6h = float(
            latest["rainfall_6h"]
        )


    if rainfall_12h is None:

        rainfall_12h = float(
            latest["rainfall_12h"]
        )


    if rainfall_24h is None:

        rainfall_24h = float(
            latest["rainfall_24h"]
        )


    if humidity is None:

        humidity = float(
            latest["humidity"]
        )


    if temperature is None:

        temperature = float(
            latest["temperature"]
        )


    # -----------------------------------------------------
    # MAIN ROUTE
    # -----------------------------------------------------

    main_route = get_osrm_route(

        start_lat,
        start_lon,

        end_lat,
        end_lon

    )


    if main_route is None:
        return None


    main_segments = create_segments(

        main_route["geometry"],

        rainfall,
        rainfall_6h,
        rainfall_12h,
        rainfall_24h,

        humidity,
        temperature

    )


    routes = []


    main_summary = summarize_route(

        main_segments,

        main_route["distance"] / 1000,

        main_route["duration"] / 60

    )


    routes.append({

        "route_id": 1,

        "recommended": False,

        "geometry": [

            [
                point[1],
                point[0]
            ]

            for point
            in main_route[
                "geometry"
            ]["coordinates"]

        ],

        **main_summary

    })


    # =====================================================
    # DETOUR ROUTES
    # =====================================================

    mid_lat = (
        start_lat + end_lat
    ) / 2

    mid_lon = (
        start_lon + end_lon
    ) / 2


    detours = [

        (
            mid_lat + 0.025,
            mid_lon - 0.020
        ),

        (
            mid_lat - 0.025,
            mid_lon + 0.020
        )

    ]


    route_id = 2


    for waypoint_lat, waypoint_lon in detours:

        waypoint_url = (

            "https://router.project-osrm.org/"
            "route/v1/driving/"

            f"{start_lon},{start_lat};"

            f"{waypoint_lon},{waypoint_lat};"

            f"{end_lon},{end_lat}"

            "?overview=full&geometries=geojson"

        )


        try:

            response = requests.get(
                waypoint_url,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()


            if data.get("code") != "Ok":
                continue


            route = data[
                "routes"
            ][0]


            segments = create_segments(

                route["geometry"],

                rainfall,
                rainfall_6h,
                rainfall_12h,
                rainfall_24h,

                humidity,
                temperature

            )


            summary = summarize_route(

                segments,

                route["distance"] / 1000,

                route["duration"] / 60

            )


            routes.append({

                "route_id": route_id,

                "recommended": False,

                "geometry": [

                    [
                        point[1],
                        point[0]
                    ]

                    for point
                    in route[
                        "geometry"
                    ]["coordinates"]

                ],

                **summary

            })


            route_id += 1


        except Exception as error:

            print(
                "Alternative route error:",
                error
            )


    # =====================================================
    # SELECT SAFEST ROUTE
    # =====================================================

    safest_route = min(

        routes,

        key=lambda route:
            route["average_risk"]

    )


    for route in routes:

        route["recommended"] = (

            route["route_id"]
            == safest_route["route_id"]

        )


    return {

        "routes": routes

    }