# ---------------------------------------------
# Charging Time
# ---------------------------------------------
def estimate_charging_time(
    battery_percentage,
    charger_power,
    battery_capacity
):

    if charger_power <= 0:
        return "Unknown"

    energy_needed = (
        (100 - battery_percentage) / 100
    ) * battery_capacity

    hours = energy_needed / charger_power

    return f"{round(hours, 2)} hours"


# ---------------------------------------------
# Charging Cost
# ---------------------------------------------
def estimate_charging_cost(
    battery_percentage,
    battery_capacity,
    cost_per_kwh
):

    if cost_per_kwh is None:
        return "Unknown"

    energy_needed = (
        (100 - battery_percentage) / 100
    ) * battery_capacity

    cost = energy_needed * cost_per_kwh

    return f"₹{round(cost, 2)}"


# ---------------------------------------------
# Waiting Time
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

    distance = station.get("distance", 5)
    score -= distance * 5

    if battery_percentage < 20:
        score -= distance * 3

    elif battery_percentage < 40:
        score -= distance * 1.5

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

    operator = station.get("operator", "").lower()

    trusted = [
        "chargezone",
        "tata",
        "statiq",
        "eesl"
    ]

    if any(op in operator for op in trusted):
        score += 10

    if station.get("status") == "Operational":
        score += 10

    if station.get("access") == "Public":
        score += 5

    number_of_points = station.get(
        "number_of_points",
        1
    )

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
def recommend_station(
    stations,
    battery_percentage,
    battery_capacity,
    user_cost_per_kwh
):

    if not stations:
        return {
            "message": "No charging stations found."
        }

    for station in stations:

        # Numeric distance for calculations
        numeric_distance = station.get("distance", 5)

        station["distance"] = (
            f"{round(numeric_distance,2)} km"
        )

        station["score"] = calculate_score(
            {
                **station,
                "distance": numeric_distance
            },
            battery_percentage
        )

        station["estimated_charging_time"] = (
            estimate_charging_time(
                battery_percentage,
                station.get("max_power_kw", 0),
                battery_capacity
            )
        )

        # Prefer API tariff
        cost_per_kwh = station.get("cost_per_kwh")

        if cost_per_kwh is None:
            cost_per_kwh = user_cost_per_kwh

        station["estimated_charging_cost"] = (
            estimate_charging_cost(
                battery_percentage,
                battery_capacity,
                cost_per_kwh
            )
        )

        station["estimated_waiting_time"] = (
            estimate_waiting_time(
                station.get("number_of_points", 1)
            )
        )
    # Sort stations by recommendation score
    stations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    best_station = stations[0]

    #remove internal fields
    best_station.pop("score", None)
    best_station.pop("latitude", None)
    best_station.pop("longitude", None)

    # Remove cost_per_kwh if not available
    if best_station.get("usage_cost") == "Not Available":
        best_station.pop("usage_cost", None)

    return best_station


    