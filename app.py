from flask import Flask, render_template, request
import numpy as np
import joblib
import os

app = Flask(__name__)

# -----------------------------
# Paths to your model and encoder
# -----------------------------
MODEL_PATH = "models\my_model.pkl"
LABEL_ENCODER_PATH = "models\label_encoder.pkl"

# -----------------------------
# Load model & label encoder
# -----------------------------
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    raise FileNotFoundError(f"{MODEL_PATH} not found!")

if os.path.exists(LABEL_ENCODER_PATH):
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
else:
    label_encoder = None
    print("⚠ label_encoder.pkl NOT found — predictions will be numeric.")

# -----------------------------
# Feature order (must match training)
# -----------------------------
FEATURE_ORDER = [
    "Age",
    "Heart_Rate_bpm",
    "Body_Temperature_C",
    "Oxygen_Saturation_%",
    "Gender_Male",
    "Systolic",
    "Diastolic",
    "Body ache",
    "Cough",
    "Fatigue",
    "Fever",
    "Headache",
    "Runny nose",
    "Shortness of breath",
    "Sore throat"
]

# -----------------------------
# Helpers
# -----------------------------
def to_int_flag(val):
    """Convert string/boolean-like input to 0/1."""
    if val is None:
        return 0
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("1", "true", "yes", "y", "male"):
            return 1
        if v in ("0", "false", "no", "n", "female"):
            return 0
        try:
            return int(float(v))
        except:
            return 0
    try:
        return int(val)
    except:
        return 0

def to_float_safe(val, default=0.0):
    try:
        return float(val)
    except:
        return default

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")  # create your input form in home.html

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Collect form inputs
        raw_inputs = {col: request.form.get(col, "") for col in FEATURE_ORDER}

        # Convert to numeric features array
        features = []
        for col in FEATURE_ORDER:
            if col in ["Gender_Male", "Body ache", "Cough", "Fatigue", "Fever",
                       "Headache", "Runny nose", "Shortness of breath", "Sore throat"]:
                features.append(to_int_flag(raw_inputs[col]))
            else:
                features.append(to_float_safe(raw_inputs[col]))

        X = np.array(features).reshape(1, -1)

        # Make prediction
        pred = model.predict(X)[0]

        # Decode label if label_encoder exists
        if label_encoder is not None:
            readable_pred = label_encoder.inverse_transform([pred])[0]
        else:
            readable_pred = pred

        return render_template("result.html",
                               prediction=readable_pred,
                               inputs=dict(zip(FEATURE_ORDER, features)))

    except Exception as e:
        return f"❌ Error: {str(e)}"

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
