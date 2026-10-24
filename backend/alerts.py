import os
from twilio.rest import Client


def send_sms(message_text: str, recipient: str):
    """
    Send an SMS using Twilio.

    Credentials are read from environment variables.
    """

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid:
        raise RuntimeError("TWILIO_ACCOUNT_SID is not configured.")

    if not auth_token:
        raise RuntimeError("TWILIO_AUTH_TOKEN is not configured.")

    if not twilio_number:
        raise RuntimeError("TWILIO_PHONE_NUMBER is not configured.")

    if not recipient:
        raise RuntimeError("Recipient phone number is required.")

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message_text,
        from_=twilio_number,
        to=recipient
    )

    return {
        "status": "sent",
        "message_sid": message.sid,
        "recipient": recipient
    }


def create_risk_alert(
    risk_level: str,
    route_id: str,
    average_risk: float,
    maximum_risk: float,
    dangerous_segments: int
):
    """
    Create a SafePath AI SMS alert.
    """

    if risk_level == "VERY HIGH":
        title = "VERY HIGH LANDSLIDE RISK"
    elif risk_level == "HIGH":
        title = "HIGH LANDSLIDE RISK"
    elif risk_level == "MEDIUM":
        title = "MEDIUM LANDSLIDE RISK"
    else:
        title = "LOW LANDSLIDE RISK"

    return (
        f"SafePath AI ALERT\n"
        f"{title}\n"
        f"Route: {route_id}\n"
        f"Average Risk: {average_risk:.1f}/100\n"
        f"Maximum Risk: {maximum_risk:.1f}/100\n"
        f"Dangerous Segments: {dangerous_segments}\n\n"
        f"Prototype risk alert - verify local conditions "
        f"before relying on this information."
    )