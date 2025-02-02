import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor

# Load dataset
file_path = "App/utils/mind_body_synergy.csv"
data = pd.read_csv(file_path)

# Feature definition
input_features = ["Physical_Fitness_Level", "Exercise_Hours_Per_Week", "Sleep_Hours_Per_Night", "Diet_Quality"]
target_features = [
    "Mental_Fitness_Level", "Stress_Level", "Social_Engagement_Score",
    "Depression_Score", "Anxiety_Score", "Confidence_Level", "Cleverness_Score", "Focus_Level"
]

X = data[input_features]
y = data[target_features]

# Encode categorical data
encoder_dict = {}
for col in ["Physical_Fitness_Level", "Diet_Quality"]:
    encoder = LabelEncoder()
    X[col] = encoder.fit_transform(X[col])
    encoder_dict[col] = encoder

for col in ["Mental_Fitness_Level", "Stress_Level", "Confidence_Level", "Focus_Level"]:
    encoder = LabelEncoder()
    y[col] = encoder.fit_transform(y[col])
    encoder_dict[col] = encoder

# Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
multi_output_model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
multi_output_model.fit(X_train_scaled, y_train)
