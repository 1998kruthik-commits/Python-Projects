import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# Load dataset
df = pd.read_csv("Data/arrhythmia.csv", na_values="?")

df = df.apply(pd.to_numeric, errors="coerce")

# Last column is target
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

# Handle missing values
imputer = SimpleImputer(strategy="mean")
X = imputer.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)
print(f"Accuracy: {acc:.4f}")

# Save model and imputer
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/arrhythmia_model.pkl")
joblib.dump(imputer, "models/imputer.pkl")

print("Model saved to models/arrhythmia_model.pkl")
