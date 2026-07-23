from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask import render_template
import os

app = Flask(__name__)

CORS(app)

alerts = []

IMAGE_FOLDER = "alerts"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)


@app.route("/")
def home():

    return render_template("dashboard.html")

@app.route("/api/alerts", methods=["POST"])
def add_alert():

    data = request.json

    data["in_time"] = data.get("in_time", "")
    data["out_time"] = data.get("out_time", "")

    alerts.append(data)

    print("\n========== ALERT RECEIVED ==========")
    print("Alert Type :", data["alert_type"])
    print("Location   :", data["location"])
    print("Camera ID  :", data["camera_id"])
    print("IN Time    :", data["in_time"])
    print("OUT Time   :", data["out_time"])
    print("Image      :", data["image"])
    print("====================================")

    return jsonify({
        "status": "success",
        "message": "Alert Saved"
    })


@app.route("/api/alerts", methods=["GET"])
def get_alerts():

    return jsonify(alerts)


@app.route("/api/latest", methods=["GET"])
def latest():

    if len(alerts)==0:

        return jsonify({})

    return jsonify(alerts[-1])


@app.route("/alerts/<filename>")
def image(filename):

    return send_from_directory(IMAGE_FOLDER, filename)


if __name__=="__main__":

    app.run(debug=True, port=5000)