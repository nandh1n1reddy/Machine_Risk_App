from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


MODEL_PATH = Path(__file__).with_name("risk_model.joblib")

rng = np.random.default_rng(42)
row_count = 1000

temperature = rng.uniform(40, 120, row_count)
pressure = rng.uniform(60, 180, row_count)
vibration = rng.integers(0, 3, row_count)  # Low=0, Medium=1, High=2

# Create example labels with a simple rule so the model has data to learn from.
score = (
    0.45 * ((temperature - 40) / 80)
    + 0.25 * ((pressure - 60) / 120)
    + 0.30 * (vibration / 2)
)

risk = np.select(
    [score < 0.35, score < 0.60],
    ["Low", "Medium"],
    default="High",
)

features = pd.DataFrame({
    "temperature": temperature,
    "pressure": pressure,
    "vibration": vibration,
})

x_train, x_test, y_train, y_test = train_test_split(
    features,
    risk,
    test_size=0.2,
    random_state=42,
    stratify=risk,
)

model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(x_train, y_train)

accuracy = accuracy_score(y_test, model.predict(x_test))
joblib.dump(model, MODEL_PATH)

print(f"Saved model to {MODEL_PATH}")
print(f"Example test accuracy: {accuracy:.2f}")