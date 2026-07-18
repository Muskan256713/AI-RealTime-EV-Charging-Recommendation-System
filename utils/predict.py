import joblib
import pandas as pd

# Load saved files
model = joblib.load("models/best_model.pkl")
encoders = joblib.load("models/label_encoders.pkl")

print("Models loaded successfully!")

def predict_charging_demand(
    hour,
    queue_length,
    initial_soc,
    traffic_density,
    weather_condition,
    day_of_week,
    location_type,
    vehicle_type,
    is_weekend
):
    # Create input DataFrame
    sample = pd.DataFrame({
        "hour": [hour],
        "queue_length": [queue_length],
        "initial_soc": [initial_soc],
        "traffic_density": [traffic_density],
        "weather_condition": [weather_condition],
        "day_of_week": [day_of_week],
        "location_type": [location_type],
        "vehicle_type": [vehicle_type],
        "is_weekend": [is_weekend]
    })

    # Encode categorical columns
    categorical_columns = [
        "traffic_density",
        "weather_condition",
        "day_of_week",
        "location_type",
        "vehicle_type"
    ]

    for col in categorical_columns:
        sample[col] = encoders[col].transform(sample[col])

    # Arrange columns exactly as during training
    feature_order = [
        "hour",
        "queue_length",
        "initial_soc",
        "traffic_density",
        "weather_condition",
        "day_of_week",
        "location_type",
        "vehicle_type",
        "is_weekend"
    ]

    sample = sample[feature_order]

    #Predict
    prediction = model.predict(sample)

    return float(prediction[0])


# Test
if __name__ == "__main__":

    result = predict_charging_demand(
        hour=18,
        queue_length=4,
        initial_soc=35,
        traffic_density="High",
        weather_condition="Cloudy",
        day_of_week="Monday",
        location_type="Urban",
        vehicle_type="Car",
        is_weekend=0
    )

    print(f"Predicted Charging Demand: {result:.2f}")