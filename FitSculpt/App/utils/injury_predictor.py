import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np

# Load dataset
file_path = "App/utils/injury_data.csv"
data = pd.read_csv(file_path)

# Add synthetic columns to represent the additional features
data["Gender_Factor"] = 1  # Default to 1 for training
data["Pregnancy_Factor"] = 1  # Default to 1 (not pregnant)
data["Disease_Factor"] = 1  # Default to 1 (no diseases)
data["Injury_Factor"] = 1  # Default to 1 (general injuries)

# Define features and target
X = data[[
    "Player_Age", "Player_Weight", "Player_Height", "Previous_Injuries",
    "Gender_Factor", "Pregnancy_Factor", "Disease_Factor", "Injury_Factor"
]]
y = data[["Training_Intensity", "Likelihood_of_Injury", "Recovery_Time"]]

# Split and scale data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)


def predict_injury(data):
    """
    Predict injury-related outcomes based on input data.

    Parameters:
    - data: List containing:
      [Player_Age, Player_Weight, Player_Height, Previous_Injuries,
       Gender, Is_Pregnant, Disease_Status, Disease_Count, Injury_Type]

    Returns:
    - A list containing [Training_Intensity, Likelihood_of_Injury, Recovery_Time]
    """
    # Injury recovery time dictionary (in days)
    injury_recovery_times = {
        "Fracture": (55, 60),  # Fractures take 55-60 days
        "Muscle Tear": (30, 40),  # Muscle tear recovery time
        "Ligament Tear": (40, 50),  # Ligament tear recovery time
        "Other": (20, 30)  # Generic injury recovery time
    }

    # Extract input features
    player_age, player_weight, player_height, previous_injuries, gender, is_pregnant, disease_status, disease_count, injury_type = data

    # Compute additional feature values
    gender_weight = {"Male": 1.0, "Female": 1.2, "Other": 1.1}
    gender_factor = gender_weight.get(gender, 1.0)
    pregnancy_factor = 1.3 if is_pregnant else 1.0
    disease_factor = 1 + (disease_count * 0.1)  # 10% increment per disease
    injury_factor = injury_recovery_times.get(injury_type, (20, 30))  # Default to "Other" if no match

    # Prepare the full input vector
    adjusted_input = [
        player_age, player_weight, player_height, previous_injuries,
        gender_factor, pregnancy_factor, disease_factor, injury_factor[0]
    ]

    # Scale the input and predict
    adjusted_input_scaled = scaler.transform([adjusted_input])
    predictions = model.predict(adjusted_input_scaled).tolist()[0]

    # Set recovery time from the injury recovery mapping
    recovery_time = np.random.randint(injury_factor[0], injury_factor[1])  # Randomly pick within the range

    return [
        round(predictions[0], 2),  # Training Intensity
        round(predictions[1], 2),  # Likelihood of Injury
        recovery_time,  # Recovery Time
    ]
