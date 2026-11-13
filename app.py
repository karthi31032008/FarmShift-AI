
import os
import requests
import firebase_admin
from datetime import datetime, timedelta

from flask import (
    Flask, request, jsonify, send_from_directory,
    render_template, session, redirect, url_for
)

from firebase_admin import credentials, firestore, auth

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret")

# Firebase connection
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "/etc/secrets/serviceAccountKey.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()


# HOME - Directly open FarmShift AI website
@app.route("/")
def home():
    return send_from_directory(".", "index.html")



# SIGNUP PAGE
@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")


# USERNAME TO EMAIL
@app.route("/api/auth/username-email", methods=["POST"])
def username_email():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"error": "Username required"}), 400

    users = db.collection("users").where(
        "username", "==", username
    ).limit(1).stream()

    for user in users:
        return jsonify({"email": user.to_dict().get("email")})

    return jsonify({"error": "Account not found"}), 404


# SAVE USER PROFILE AFTER FIREBASE SIGNUP
@app.route("/api/auth/profile", methods=["POST"])
def save_profile():
    data = request.get_json(silent=True) or {}

    token = request.headers.get("Authorization", "")
    if not token.startswith("Bearer "):
        return jsonify({"error": "Authentication required"}), 401

    try:
        decoded = auth.verify_id_token(token.split(" ", 1)[1])
        uid = decoded["uid"]
        email = decoded.get("email", "")
    except Exception:
        return jsonify({"error": "Invalid login token"}), 401

    username = data.get("username", "").strip()

    if not username:
        return jsonify({"error": "Username required"}), 400

    existing = db.collection("users").where(
        "username", "==", username
    ).limit(1).stream()

    for user in existing:
        if user.id != uid:
            return jsonify({"error": "Username already exists"}), 409

    db.collection("users").document(uid).set({
        "username": username,
        "email": email,
        "created_at": firestore.SERVER_TIMESTAMP
    }, merge=True)

    return jsonify({"status": "success"})


# CREATE FLASK LOGIN SESSION
@app.route("/api/auth/session", methods=["POST"])
def create_session():
    token = request.headers.get("Authorization", "")

    if not token.startswith("Bearer "):
        return jsonify({"error": "Login required"}), 401

    try:
        decoded = auth.verify_id_token(token.split(" ", 1)[1])
        session["uid"] = decoded["uid"]
        return jsonify({"status": "success"})
    except Exception:
        return jsonify({"error": "Invalid token"}), 401


@app.route("/dashboard")
def dashboard():
    return send_from_directory(".", "index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# CROP ANALYSIS API
@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}

    crop = data.get("crop", "")
    soil = data.get("soil", "")
    village = data.get("village", "")
    district = data.get("district", "")
    water = data.get("water", "")

    if not all([crop, soil, village, district, water]):
        return jsonify({"error": "Please enter all details"}), 400

    if water == "Low":
        suggestion = "Review irrigation requirements."
        vegetation = "Needs Attention"

    elif water == "Medium":
        suggestion = "Monitor soil moisture regularly."
        vegetation = "Moderate"

    else:
        suggestion = "Monitor drainage conditions."
        vegetation = "Monitor Crop Condition"

    db.collection("search_history").add({
        "crop": crop,
        "soil": soil,
        "village": village,
        "district": district,
        "water": water,
        "vegetation": vegetation,
        "recommendation": suggestion,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return jsonify({
        "status": "success",
        "village": village,
        "district": district,
        "crop": crop,
        "soil": soil,
        "water": water,
        "vegetation": vegetation,
        "recommendation": suggestion
    })


# WEATHER API
@app.route("/weather")
def weather():
    latitude = request.args.get("lat", "11.6643")
    longitude = request.args.get("lon", "78.1460")

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=15)
    return jsonify(response.json())
# NASA POWER WEATHER DATA API
@app.route("/api/nasa-weather")
def nasa_weather():

    latitude = request.args.get("lat", "11.6643")
    longitude = request.args.get("lon", "78.1460")

    try:
        latitude = float(latitude)
        longitude = float(longitude)

        if not (-90 <= latitude <= 90):
            return jsonify({"error": "Invalid latitude"}), 400

        if not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid longitude"}), 400

        end_date = datetime.utcnow().date() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)

        url = "https://power.larc.nasa.gov/api/temporal/daily/point"

        params = {
            "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M",
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d"),
            "format": "JSON"
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        nasa_data = response.json()

        weather_data = nasa_data["properties"]["parameter"]

        return jsonify({
            "status": "success",
            "source": "NASA POWER",
            "latitude": latitude,
            "longitude": longitude,
            "data": weather_data
        })

    except requests.RequestException:
        return jsonify({
            "error": "NASA service unavailable"
        }), 503

    except (ValueError, KeyError, TypeError):
        return jsonify({
            "error": "Unable to process NASA data"
        }), 500
        
@app.route('/satellite')
def satellite():
    return render_template('satellite.html')
    
@app.route('/weather-dashboard')
def weather_dashboard():
    return render_template('weather.html')


@app.route('/crop')
def crop():
    return render_template('crop.html')


@app.route('/ai-recommendation')
def ai_recommendation():
    return render_template('ai-recommendation.html')
    


# START SERVER - ALWAYS KEEP THIS AT THE END
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
