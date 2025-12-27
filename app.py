from flask import Flask, request, jsonify, render_template
import joblib, pandas as pd, os
from datetime import datetime

app = Flask(__name__)

# Load model and pipeline
pipeline = joblib.load("full_pipeline_model.pkl")

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "prediction_logs.csv")

os.makedirs(LOG_DIR, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")  # Flask looks in templates/

# single prediction endpoint
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    df = pd.DataFrame([data])
    probs = pipeline.predict_proba(df)
    pred = pipeline.predict(df)[0]
    message = "Will pay back" if pred == 1 else "Will not pay back"
    response = {
        "prediction": message,
        "probability_paid_back": float(probs[0][1]),
        "probability_not_paid_back": float(probs[0][0])
    }
    return jsonify(response)

# CSV batch prediction endpoint
@app.route("/predict_csv", methods=["POST"])
def predict_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    try:
        df = pd.read_csv(file)

        # Safety: drop target if accidentally included
        if "loan_paid_back" in df.columns:
            df = df.drop(columns=["loan_paid_back"])

        # DO NOT select columns manually
        probs = pipeline.predict_proba(df)
        preds = pipeline.predict(df)

        df["prediction"] = [
            "Will pay back" if p == 1 else "Will not pay back"
            for p in preds
        ]
        df["probability_paid_back"] = probs[:, 1]
        df["probability_not_paid_back"] = probs[:, 0]
        df["timestamp"] = datetime.now()

        # Logging
        os.makedirs("logs", exist_ok=True)
        df.to_csv(LOG_FILE, mode="a", header=not os.path.exists(LOG_FILE), index=False)

        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify([])

        df = pd.read_csv(LOG_FILE)

        # Keep only what frontend needs
        keep_cols = [
            "prediction",
            "probability_paid_back",
            "probability_not_paid_back",
            "credit_score",
            "loan_amount"
        ]
        df = df[[c for c in keep_cols if c in df.columns]]

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        print("LOG ERROR:", e)
        return jsonify([]), 200


if __name__ == "__main__":
    app.run(debug=True)
