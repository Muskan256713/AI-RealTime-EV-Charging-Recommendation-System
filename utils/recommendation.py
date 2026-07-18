BATTERY_CAPACITY = 50      # kWh
COST_PER_KWH = 8           # ₹


# ---------------------------------------------
# Charging Time
# ---------------------------------------------
def estimate_charging_time(battery_percentage, charger_power):

    if charger_power <= 0:
        return "Unknown"

    energy_needed = (100 - battery_percentage) / 100 * BATTERY_CAPACITY

    hours = energy_needed / charger_power

    return f"{round(hours, 2)} hours"


# ---------------------------------------------
# Charging Cost
# ---------------------------------------------
def estimate_charging_cost(battery_percentage):

    energy_needed = (100 - battery_percentage) / 100 * BATTERY_CAPACITY

    cost = energy_needed * COST_PER_KWH

    return f"₹{round(cost, 2)}"


# ---------------------------------------------
# Waiting Time (Estimated)
# ---------------------------------------------
def estimate_waiting_time(number_of_points):

    if number_of_points >= 6:
        waiting = 2

    elif number_of_points >= 4:
        waiting = 5

    elif number_of_points >= 2:
        waiting = 10

    else:
        waiting = 15

    return f"{waiting} min"


# ---------------------------------------------
# Recommendation Score
# ---------------------------------------------
def calculate_score(station, battery_percentage):

    score = 100

    # Distance
    distance = station.get("distance", 5)
    score -= distance * 5

    # Battery Priority
    if battery_percentage < 20:
        score -= distance * 3

    elif battery_percentage < 40:
        score -= distance * 1.5

    # Charger Power
    power = station.get("max_power_kw", 0)

    if power >= 120:
        score += 30

    elif power >= 60:
        score += 25

    elif power >= 30:
        score += 15

    elif power >= 15:
        score += 8

    else:
        score -= 5

    # Trusted Operator
    operator = station.get("operator", "").lower()

    trusted = [
        "chargezone",
        "tata",
        "statiq",
        "eesl"
    ]

    if any(op in operator for op in trusted):
        score += 10

    # Operational
    if station.get("status") == "Operational":
        score += 10

    # Public Access
    if station.get("access") == "Public":
        score += 5

    # Waiting Time Penalty
    number_of_points = station.get("number_of_points", 1)

    if number_of_points >= 6:
        waiting_minutes = 2
    elif number_of_points >= 4:
        waiting_minutes = 5
    elif number_of_points >= 2:
        waiting_minutes = 10
    else:
        waiting_minutes = 15

    score -= waiting_minutes * 0.5

    return round(score, 2)


# ---------------------------------------------
# Recommendation Engine
# ---------------------------------------------
def recommend_station(stations, battery_percentage):

    if not stations:
        return {
            "message": "No charging stations found."
        }

    for station in stations:

        # Keep numeric distance for calculations
        if station.get("distance") is not None:
            numeric_distance = station["distance"]
            station["distance"] = f"{round(numeric_distance, 2)} km"

        station["score"] = calculate_score(
            {
                **station,
                "distance": numeric_distance if 'numeric_distance' in locals() else 5
            },
            battery_percentage
        )

        station["estimated_charging_time"] = estimate_charging_time(
            battery_percentage,
            station.get("max_power_kw", 0)
        )

        station["estimated_charging_cost"] = estimate_charging_cost(
            battery_percentage
        )

        station["estimated_waiting_time"] = estimate_waiting_time(
            station.get("number_of_points", 1)
        )

    stations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return stations[0]