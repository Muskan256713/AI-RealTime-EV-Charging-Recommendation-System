import os
import openrouteservice
from dotenv import load_dotenv

# Load API Key
load_dotenv()

API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

client = openrouteservice.Client(key=API_KEY)


def get_route(source_lat,
              source_lon,
              dest_lat,
              dest_lon):

    """
    Returns real driving distance and travel duration
    using OpenRouteService API.
    """

    coordinates = [
        (source_lon, source_lat),
        (dest_lon, dest_lat)
    ]

    route = client.directions(
        coordinates=coordinates,
        profile="driving-car",
        format="geojson"
    )

    summary = route["features"][0]["properties"]["summary"]

    distance_km = round(summary["distance"] / 1000, 2)
    duration_min = round(summary["duration"] / 60, 2)

    return {
        "travel_distance": f"{distance_km} km",
        "travel_duration": f"{duration_min} min"
    }