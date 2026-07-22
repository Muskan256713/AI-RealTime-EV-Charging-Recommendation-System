import os
import re
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENCHARGEMAP_API_KEY")

BASE_URL = "https://api.openchargemap.io/v3/poi/"


# -----------------------------------------------------
# Extract numeric charging cost from UsageCost
# -----------------------------------------------------
def extract_cost_per_kwh(usage_cost):

    if not usage_cost:
        return None

    usage_cost = usage_cost.lower()

    # Extract first numeric value
    match = re.search(r"(\d+(\.\d+)?)", usage_cost)

    if match:
        return float(match.group(1))

    return None


# -----------------------------------------------------
# Fetch Nearby Charging Stations
# -----------------------------------------------------
def get_nearby_stations(latitude, longitude, distance=5):

    params = {
        "key": API_KEY,
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance,
        "distanceunit": "KM",
        "maxresults": 10
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print("Error:", response.status_code)
        print("Response:", response.text)
        return []

    data = response.json()

    stations = []

    for station in data:

        connections = station.get("Connections", [])

        max_power = 0
        connector_types = []

        for conn in connections:

            power = conn.get("PowerKW")

            if power:
                max_power = max(max_power, power)

            connection = conn.get("ConnectionType")

            if connection:
                connector_types.append(
                    connection.get("Title", "Unknown")
                )

        usage_cost = (
            station.get("UsageCost")
            if station.get("UsageCost")
            else "Unknown"
        )

        cost_per_kwh = extract_cost_per_kwh(usage_cost)

        stations.append({

            "name": station.get("AddressInfo", {}).get("Title"),

            "address": station.get("AddressInfo", {}).get("AddressLine1"),

            "distance": round(
                station.get("AddressInfo", {}).get("Distance", 0),
                2
            ),

            "latitude": station.get("AddressInfo", {}).get("Latitude"),

            "longitude": station.get("AddressInfo", {}).get("Longitude"),

            "operator": (
                station.get("OperatorInfo", {}).get("Title")
                if station.get("OperatorInfo")
                else "Unknown"
            ),

            "number_of_points": station.get("NumberOfPoints", 1),

            "max_power_kw": max_power,

            "connector_types": connector_types,

            "usage_cost": usage_cost,

            "cost_per_kwh": cost_per_kwh,

            "status": (
                station.get("StatusType", {}).get("Title")
                if station.get("StatusType")
                else "Unknown"
            ),

            "access": (
                station.get("UsageType", {}).get("Title")
                if station.get("UsageType")
                else "Unknown"
            )
        })

    return stations