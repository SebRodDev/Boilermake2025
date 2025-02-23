import pandas as pd
import joblib
import os

# Check for model and scaler files
if not os.path.exists("logistic_model.pkl"):
    raise FileNotFoundError("logistic_model.pkl not found.")
if not os.path.exists("scaler.pkl"):
    raise FileNotFoundError("scaler.pkl not found.")

# Load the saved model and scaler
model = joblib.load("logistic_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load new incomplete synthetic data
try:
    incomplete_data = pd.read_parquet("student_grades.parquet")
    print(f"Loaded incomplete data with {len(incomplete_data)} rows.")
    print(incomplete_data.head())
except FileNotFoundError:
    print("Error: synthetic_incomplete_data.parquet not found.")
    exit()  # Exit if file not found

# Fill missing values
incomplete_data = incomplete_data.fillna(0)

# Verify columns in incomplete_data
print("Incomplete data columns:", incomplete_data.columns.tolist())

# Create the interaction term
incomplete_data["grade_week_interaction"] = incomplete_data["current_grade"] * incomplete_data["week"]

# Define the expected features
features = ["homework_avg", "quiz_avg", "current_grade", "week", "grade_week_interaction"]

# Check for missing columns
missing_cols = set(features) - set(incomplete_data.columns)
if missing_cols:
    raise ValueError(f"Missing columns in the incomplete data: {missing_cols}")

# Ensure columns are numeric
X_new = incomplete_data[features][features].apply(pd.to_numeric, errors="coerce")
if X_new.isnull().any().any():
    print("Warning: There are still NaNs in the feature columns after conversion.")

# Scale the features
X_new_scaled = scaler.transform(X_new)

# Predict failure probabilities
failure_probs = model.predict_proba(X_new_scaled)[:, 1]
incomplete_data["failing_probability"] = failure_probs

print(incomplete_data.head())