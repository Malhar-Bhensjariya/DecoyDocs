from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import os
import joblib

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "models", "xgb_bot_model.pkl")
scaler_path = os.path.join(BASE_DIR, "models", "scaler.pkl")

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)


FEATURES = [
    "mean_speed",
    "std_speed",
    "max_speed",
    "mean_angle_change"
]

def extract_window_features(coords):
    dx = np.diff(coords[:,0])
    dy = np.diff(coords[:,1])

    dist = np.sqrt(dx**2 + dy**2)
    angles = np.arctan2(dy, dx)
    angle_diff = np.diff(angles)

    straight = np.linalg.norm(coords[-1] - coords[0])
    path_len = dist.sum() + 1e-6

    return [
        dist.mean(),
        dist.std(),
        dist.max(),
        np.abs(angle_diff).mean() if len(angle_diff) else 0
    ]

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    coords = np.array(data["coords"])

    if len(coords) < 5:
        return jsonify({"error": "Not enough data"}), 400

    features = np.array(extract_window_features(coords)).reshape(1, -1)
    features_scaled = scaler.transform(features)

    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0][1]

    return jsonify({
        "prediction": int(prediction),
        "probability_human": float(probability),
        "result": "Human" if prediction == 1 else "Bot"
    })

if __name__ == "__main__":
    app.run(debug=True)
