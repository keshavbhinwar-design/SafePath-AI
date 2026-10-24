from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import joblib
import requests
import pandas as pd
import os

from dotenv import load_dotenv

from backend.terrain import get_terrain
from backend.route_segments import analyze_route_options
from backend.alerts import send_sms, create_risk_alert


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# SAFEPATH AI - FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="SafePath AI",
    description="AI-powered landslide risk and safer routing system"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

model = joblib.load(
    "ml/landslide_model.pkl"
)


# ============================================================
# INPUT MODELS
# ============================================================

class RiskInput(BaseModel):
    rainfall: float
    humidity: float
    temperature: float
    elevation: float
    slope: float


class LocationInput(BaseModel):

    start_lat: float
    start_lon: float

    end_lat: float
    end_lon: float

    # Optional weather simulation inputs

    rainfall: float | None = None
    rainfall_6h: float | None = None
    rainfall_12h: float | None = None
    rainfall_24h: float | None = None

    humidity: float | None = None
    temperature: float | None = None


class AlertInput(BaseModel):

    risk_level: str
    route_id: str
    average_risk: float
    maximum_risk: float
    dangerous_segments: int
    recipient: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "project": "SafePath AI",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# PREDICT RISK
# ============================================================

@app.post("/predict-risk")
def predict_risk(data: RiskInput):

    input_data = [[
        data.rainfall,
        data.humidity,
        data.temperature,
        data.elevation,
        data.slope
    ]]

    prediction = model.predict(
        input_data
    )[0]

    probability = model.predict_proba(
        input_data
    )[0][1]

    risk_score = probability * 100

    if risk_score <= 30:

        risk_level = "LOW"

    elif risk_score <= 60:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"

    return {

        "risk_score": round(
            risk_score,
            2
        ),

        "risk_level": risk_level,

        "landslide_prediction": int(
            prediction
        )
    }


# ============================================================
# NORMAL ROUTE
# ============================================================

@app.post("/route")
def get_route(data: LocationInput):

    url = (
        "https://router.project-osrm.org/"
        "route/v1/driving/"
        f"{data.start_lon},{data.start_lat};"
        f"{data.end_lon},{data.end_lat}"
        "?overview=full&geometries=geojson"
    )

    response = requests.get(
        url,
        timeout=20
    )

    if response.status_code != 200:

        return {
            "status": "error",
            "message": "Routing service unavailable"
        }

    result = response.json()

    if result["code"] != "Ok":

        return {
            "status": "error",
            "message": "No route found"
        }

    route = result["routes"][0]

    return {

        "status": "success",

        "distance_km": round(
            route["distance"] / 1000,
            2
        ),

        "duration_minutes": round(
            route["duration"] / 60,
            2
        ),

        "route": route["geometry"]
    }


# ============================================================
# SAFE ROUTE
# ============================================================

@app.post("/safe-route")
def safe_route(data: LocationInput):

    url = (
        "https://router.project-osrm.org/"
        "route/v1/driving/"
        f"{data.start_lon},{data.start_lat};"
        f"{data.end_lon},{data.end_lat}"
        "?overview=full&geometries=geojson"
    )

    response = requests.get(
        url,
        timeout=20
    )

    if response.status_code != 200:

        return {
            "status": "error",
            "message": "Routing service unavailable"
        }

    result = response.json()

    if result["code"] != "Ok":

        return {
            "status": "error",
            "message": "No route found"
        }

    route = result["routes"][0]


    # ========================================================
    # WEATHER
    # ========================================================

    weather = pd.read_csv(
        "data/weather.csv"
    )

    latest = weather.iloc[0]

    rainfall = float(
        latest["rainfall"]
    )

    humidity = float(
        latest["humidity"]
    )

    temperature = float(
        latest["temperature"]
    )


    # ========================================================
    # TEMPORARY DEMO TERRAIN
    # ========================================================

    elevation = 1100

    slope = 10


    # ========================================================
    # ML PREDICTION
    # ========================================================

    input_data = [[
        rainfall,
        humidity,
        temperature,
        elevation,
        slope
    ]]

    prediction = model.predict(
        input_data
    )[0]

    probability = model.predict_proba(
        input_data
    )[0][1]

    risk_score = probability * 100

    if risk_score <= 30:

        risk_level = "LOW"

    elif risk_score <= 60:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"


    return {

        "status": "success",

        "route": {

            "distance_km": round(
                route["distance"] / 1000,
                2
            ),

            "duration_minutes": round(
                route["duration"] / 60,
                2
            ),

            "geometry": route["geometry"]
        },

        "risk": {

            "score": round(
                risk_score,
                2
            ),

            "level": risk_level,

            "landslide_prediction": int(
                prediction
            )
        },

        "weather": {

            "rainfall_mm": rainfall,

            "humidity_percent": humidity,

            "temperature_c": temperature
        },

        "terrain": {

            "elevation_m": elevation,

            "slope_degrees": slope
        }
    }


# ============================================================
# ROUTE SEGMENT ANALYSIS + AUTOMATIC ALERT
# ============================================================

@app.post("/route-segments")
def route_segments(
    data: LocationInput,
    background_tasks: BackgroundTasks
):

    # ========================================================
    # ANALYZE ROUTES
    # ========================================================

    routes = analyze_route_options(

        data.start_lat,

        data.start_lon,

        data.end_lat,

        data.end_lon,

        rainfall=data.rainfall,

        rainfall_6h=data.rainfall_6h,

        rainfall_12h=data.rainfall_12h,

        rainfall_24h=data.rainfall_24h,

        humidity=data.humidity,

        temperature=data.temperature
    )


    if routes is None:

        return {

            "status": "error",

            "message":
                "Unable to generate routes"
        }


    # ========================================================
    # LOAD WEATHER DATA
    # ========================================================

    weather = pd.read_csv(
        "data/weather.csv"
    )

    latest = weather.iloc[0]


    # ========================================================
    # WEATHER VALUES
    # ========================================================

    if data.rainfall is not None:

        rainfall = data.rainfall

    else:

        rainfall = float(
            latest["rainfall"]
        )


    if data.rainfall_6h is not None:

        rainfall_6h = data.rainfall_6h

    else:

        rainfall_6h = float(
            latest["rainfall_6h"]
        )


    if data.rainfall_12h is not None:

        rainfall_12h = data.rainfall_12h

    else:

        rainfall_12h = float(
            latest["rainfall_12h"]
        )


    if data.rainfall_24h is not None:

        rainfall_24h = data.rainfall_24h

    else:

        rainfall_24h = float(
            latest["rainfall_24h"]
        )


    if data.humidity is not None:

        humidity = data.humidity

    else:

        humidity = float(
            latest["humidity"]
        )


    if data.temperature is not None:

        temperature = data.temperature

    else:

        temperature = float(
            latest["temperature"]
        )


    # ========================================================
    # TERRAIN
    # ========================================================

    elevation, slope = get_terrain(

        data.start_lat,

        data.start_lon
    )


    # ========================================================
    # AUTOMATIC SMS ALERT
    # ========================================================

    alert_status = "not_triggered"

    alert_message = None


    # --------------------------------------------------------
    # Find the recommended/safest route
    # --------------------------------------------------------

    recommended_route = None

    if isinstance(routes, list) and len(routes) > 0:

        for route in routes:

            if route.get("recommended") is True:

                recommended_route = route
                break

        # Fallback: use first route if no explicit
        # recommended flag exists

        if recommended_route is None:

            recommended_route = routes[0]


    # --------------------------------------------------------
    # Check recommended route risk
    # --------------------------------------------------------

    if recommended_route is not None:

        risk_level = str(
            recommended_route.get(
                "risk_level",
                recommended_route.get(
                    "level",
                    "LOW"
                )
            )
        ).upper()


        average_risk = float(
            recommended_route.get(
                "average_risk",
                recommended_route.get(
                    "risk",
                    0
                )
            )
        )


        maximum_risk = float(
            recommended_route.get(
                "maximum_risk",
                recommended_route.get(
                    "max_risk",
                    average_risk
                )
            )
        )


        dangerous_segments = int(
            recommended_route.get(
                "dangerous_segments",
                0
            )
        )


        route_id = str(
            recommended_route.get(
                "route_id",
                recommended_route.get(
                    "id",
                    "Recommended Route"
                )
            )
        )


        # ----------------------------------------------------
        # Trigger only for HIGH / VERY HIGH
        # ----------------------------------------------------

        if risk_level in ["HIGH", "VERY HIGH"]:

            recipient = os.getenv(
                "SAFEPATH_ALERT_NUMBER"
            )


            if recipient:

                message = create_risk_alert(

                    risk_level=risk_level,

                    route_id=route_id,

                    average_risk=average_risk,

                    maximum_risk=maximum_risk,

                    dangerous_segments=dangerous_segments
                )


                background_tasks.add_task(

                    send_sms,

                    message,

                    recipient
                )


                alert_status = "queued"

                alert_message = (
                    "Prototype SMS risk alert "
                    "has been queued."
                )

            else:

                alert_status = "not_configured"

                alert_message = (
                    "High risk detected, but "
                    "SAFEPATH_ALERT_NUMBER is "
                    "not configured in .env."
                )


        else:

            alert_status = "not_triggered"

            alert_message = (
                "No SMS alert required. "
                "Recommended route risk is "
                f"{risk_level}."
            )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "status": "success",

        "routes": routes,

        "alert": {

            "status": alert_status,

            "message": alert_message
        },

        "weather": {

            "rainfall": rainfall,

            "rainfall_6h": rainfall_6h,

            "rainfall_12h": rainfall_12h,

            "rainfall_24h": rainfall_24h,

            "humidity": humidity,

            "temperature": temperature
        },

        "terrain": {

            "elevation": (

                round(
                    elevation,
                    2
                )

                if elevation is not None

                else None
            ),

            "slope": (

                round(
                    slope,
                    2
                )

                if slope is not None

                else None
            )
        }
    }


# ============================================================
# MANUAL SMS ALERT
# ============================================================

@app.post("/send-alert")
def send_alert(

    data: AlertInput,

    background_tasks: BackgroundTasks

):

    # ========================================================
    # ONLY HIGH / VERY HIGH RISK
    # ========================================================

    if data.risk_level not in [

        "HIGH",

        "VERY HIGH"

    ]:

        return {

            "status": "not_sent",

            "message":
                "SMS alert is only triggered "
                "for HIGH or VERY HIGH risk."
        }


    # ========================================================
    # CREATE ALERT MESSAGE
    # ========================================================

    message = create_risk_alert(

        risk_level=data.risk_level,

        route_id=data.route_id,

        average_risk=data.average_risk,

        maximum_risk=data.maximum_risk,

        dangerous_segments=data.dangerous_segments
    )


    # ========================================================
    # QUEUE SMS
    # ========================================================

    background_tasks.add_task(

        send_sms,

        message,

        data.recipient
    )


    return {

        "status": "queued",

        "message":
            "Risk alert SMS has been queued."
    }