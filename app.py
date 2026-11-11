
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
    water = data.get("water", "")

    if not crop or not soil or not water:
        return jsonify({"error": "Please enter all details"}), 400

    if water == "Low":
        suggestion = "Review irrigation requirements."
    elif water == "Medium":
        suggestion = "Monitor soil moisture regularly."
    else:
        suggestion = "Monitor drainage conditions."

    return jsonify({
        "status": "success",
        "crop": crop,
        "soil": soil,
        "water": water,
        "recommendation": suggestion
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
  
