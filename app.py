
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate(
        "/etc/secrets/serviceAccountKey.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

db = firestore.client()
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    crop = data.get("crop", "")
    soil = data.get("soil", "")
    village = data.get("village", "")
    district = data.get("district", "")
    water = data.get("water", "")

    if not crop or not soil or not village or not district or not water:
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
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
  

import requests

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

    response = requests.get(url, params=params)
    return jsonify(response.json())
