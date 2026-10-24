def calculate_risk_score(rainfall, humidity, slope, elevation):
    """
    Calculate a synthetic landslide risk score from 0 to 100.

    NOTE:
    This is a prototype scoring system using synthetic data.
    It is NOT a real-world landslide warning model.
    """

    # Rainfall contribution: 0–40
    rainfall_score = min(rainfall / 50 * 40, 40)

    # Slope contribution: 0–30
    slope_score = min(slope / 45 * 30, 30)

    # Humidity contribution: 0–20
    humidity_score = min(humidity / 100 * 20, 20)

    # Elevation contribution: 0–10
    elevation_score = min(elevation / 1600 * 10, 10)

    # Total score
    score = (
        rainfall_score
        + slope_score
        + humidity_score
        + elevation_score
    )

    score = min(score, 100)

    # Risk category
    if score <= 30:
        risk = "LOW"
    elif score <= 60:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    return round(score, 2), risk


# Test example
score, risk = calculate_risk_score(
    rainfall=20,
    humidity=85,
    slope=30,
    elevation=1100
)

print("===== SafePath AI Risk Assessment =====")
print("Risk Score:", score, "/ 100")
print("Risk Level:", risk)