import requests
from geopy.distance import geodesic
from modules.audio_feedback import speak

OSRM_URL = "http://router.project-osrm.org/route/v1/walking"

def get_route(start, end):
    """
    start, end = (lat, lon)
    """
    url = f"{OSRM_URL}/{start[1]},{start[0]};{end[1]},{end[0]}"
    params = {
        "overview": "false",
        "steps": "true"
    }

    response = requests.get(url, params=params)
    data = response.json()

    steps = data["routes"][0]["legs"][0]["steps"]
    return steps


def start_navigation(start, destination):
    speak("GPS navigation started")

    steps = get_route(start, destination)

    for step in steps:
        maneuver = step.get("maneuver", {})
        m_type = maneuver.get("type", "move")
        modifier = maneuver.get("modifier", "")

        road = step.get("name", "")
        distance = int(step.get("distance", 0))

        instruction = f"{m_type} {modifier}".strip()

        if road:
            instruction += f" onto {road}"

        speak(f"{instruction}. Walk {distance} meters.")


if __name__ == "__main__":
    # Test coordinates (Bangalore example)
    start_location = (12.9716, 77.5946)
    destination = (12.9763, 77.6033)

    start_navigation(start_location, destination)
