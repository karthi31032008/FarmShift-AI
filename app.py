
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

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
  
