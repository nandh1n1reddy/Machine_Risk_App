from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).with_name("risk_model.joblib")
FEATURES = ["temperature", "pressure", "vibration"]
VIBRATION_CODES = {"Low": 0, "Medium": 1, "High": 2}


def predict_risk(machine_data: dict) -> dict:
    missing = [
        key for key in FEATURES
        if machine_data.get(key) in (None, "")
    ]
    if missing:
        raise ValueError(
            "Missing model inputs: " + ", ".join(missing)
        )

    if not MODEL_PATH.exists():
        raise ValueError(
            "Model file is missing. Run: python -m ml.train_model"
        )

    try:
        temperature = float(machine_data["temperature"])
        pressure = float(machine_data["pressure"])
    except (TypeError, ValueError):
        raise ValueError("Temperature and Pressure must be numbers.")

    vibration = machine_data["vibration"]
    if vibration not in VIBRATION_CODES:
        raise ValueError(
            "Vibration must be Low, Medium, or High."
        )

    model_input = pd.DataFrame([{
        "temperature": temperature,
        "pressure": pressure,
        "vibration": VIBRATION_CODES[vibration],
    }])

    model = joblib.load(MODEL_PATH)
    risk_level = str(model.predict(model_input)[0])

    ignored_fields = sorted(
        key for key, value in machine_data.items()
        if key not in FEATURES and value not in (None, "")
    )

    return {
        "risk_level": risk_level,
        "features_used": FEATURES,
        "ignored_fields": ignored_fields,
    }