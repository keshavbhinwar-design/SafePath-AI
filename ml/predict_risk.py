import joblib
import pandas as pd

# Load trained model
model = joblib.load("ml/landslide_model.pkl")

# Example current conditions
data = pd.DataFrame([{
    "rainfall": 20,
    "humidity": 85,
    "temperature": 24,
    "elevation": 1100,
    "slope": 30
}])

# Prediction
prediction = model.predict(data)[0]

# Probability
probability = model.predict_proba(data)[0][1]

print("===== SafePath AI =====")

if prediction == 1:
    print("⚠️ Landslide risk detected")
else:
    print("✅ Low landslide risk")

print("Risk probability:", round(probability * 100, 2), "%")