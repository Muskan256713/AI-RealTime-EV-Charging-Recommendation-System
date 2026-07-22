from fastapi import FastAPI
from pydantic import BaseModel

from utils.predict import predict_charging_demand
from services.openchargemap import get_nearby_stations
from services.route_service import get_route
from utils.recommendation import recommend_station

app = FastAPI(
    title="AI-Based EV Charging Recommendation API",
    version="2.0"
)


# ----------------------------------------------------
# Input Schema
# ----------------------------------------------------

class ChargingRequest(BaseModel):
    hour: int
    queue_length: int
    initial_soc: float
    traffic_density: str
    weather_condition: str
    day_of_week: str
    location_type: str
    vehicle_type: str
    is_weekend: int

    latitude: float
    longitude: float

    battery_capacity: float      # kWh
    cost_per_kwh: float          # ₹/kWh


# ----------------------------------------------------
# Home Endpoint
# ----------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI-Based Real-Time EV Charging Recommendation API is Running!"
    }


# ----------------------------------------------------
# Prediction Endpoint
# ----------------------------------------------------

@app.post("/predict")
def predict(request: ChargingRequest):

    try:

        # ----------------------------------------------------
        # Predict Charging Demand
        # ----------------------------------------------------

        prediction = predict_charging_demand(
            hour=request.hour,
            queue_length=request.queue_length,
            initial_soc=request.initial_soc,
            traffic_density=request.traffic_density,
            weather_condition=request.weather_condition,
            day_of_week=request.day_of_week,
            location_type=request.location_type,
            vehicle_type=request.vehicle_type,
            is_weekend=request.is_weekend
        )

        # ----------------------------------------------------
        # Fetch Nearby Charging Stations
        # ----------------------------------------------------

        stations = get_nearby_stations(
            latitude=request.latitude,
            longitude=request.longitude
        )

        # ----------------------------------------------------
        # Calculate Real Route
        # ----------------------------------------------------

        for station in stations:

            route = get_route(
                source_lat=request.latitude,
                source_lon=request.longitude,
                dest_lat=station["latitude"],
                dest_lon=station["longitude"]
            )

            station["travel_distance"] = route["travel_distance"]
            station["travel_time"] = route["travel_duration"]

        # ----------------------------------------------------
        # Recommend Best Station
        # ----------------------------------------------------

        best_station = recommend_station(
            stations=stations,
            battery_percentage=request.initial_soc,
            battery_capacity=request.battery_capacity,
            user_cost_per_kwh=request.cost_per_kwh
        )

        # ----------------------------------------------------
        # Final Response
        # ----------------------------------------------------

        return {
            "Predicted Charging Demand": f"{round(prediction, 2)} %",
            "Recommended Station": best_station
        }

    except Exception as e:
        import traceback

        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }