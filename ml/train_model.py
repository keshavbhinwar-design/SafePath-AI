import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
data = pd.read_csv("data/landslide_dataset.csv")

# Features used by the model
features = [
    "rainfall",
    "humidity",
    "temperature",
    "elevation",
    "slope"
]

X = data[features]
y = data["landslide"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Create model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Test
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("SafePath AI model trained!")
print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Save model
joblib.dump(model, "ml/landslide_model.pkl")

print("\nModel saved to:")
print("ml/landslide_model.pkl")