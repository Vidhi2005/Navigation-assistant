from flask import Flask, request, jsonify

app = Flask(__name__)

# Shared GPS state (same process only)
current_location = None


@app.route("/location", methods=["POST"])
def receive_location():
    global current_location

    # Safety check
    if not request.is_json:
        return jsonify({"error": "JSON data required"}), 400

    data = request.get_json()

    # Validate keys
    if "lat" not in data or "lon" not in data:
        return jsonify({"error": "lat and lon required"}), 400

    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
    except ValueError:
        return jsonify({"error": "lat and lon must be numbers"}), 400

    current_location = (lat, lon)

    print("📍 Live GPS received:", current_location)

    return jsonify({"status": "Location updated"}), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "current_location": current_location,
        "gps_active": current_location is not None
    })


def get_current_location():
    """
    Used by navigation module
    Must be called in the SAME process
    """
    return current_location


if __name__ == "__main__":
    print("🚀 Live GPS server started")
    app.run(host="0.0.0.0", port=5000)
