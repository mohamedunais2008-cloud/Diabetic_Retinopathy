"""
Rural Geolocation & Referral Routing Service
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import math

# Sample Directory of Tertiary Eye Care Referral Centers in India
TERTIARY_EYE_CENTERS = [
    {
        "name": "Aravind Eye Hospital - Madurai",
        "district": "Madurai",
        "state": "Tamil Nadu",
        "lat": 9.9252,
        "lon": 78.1198,
        "phone": "+91 452 435 6100",
        "has_retina_specialist": True,
        "laser_available": True
    },
    {
        "name": "Sankara Nethralaya - Chennai",
        "district": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0604,
        "lon": 80.2496,
        "phone": "+91 44 4227 1500",
        "has_retina_specialist": True,
        "laser_available": True
    },
    {
        "name": "Dr. Rajendra Prasad Centre for Ophthalmic Sciences (AIIMS)",
        "district": "New Delhi",
        "state": "Delhi",
        "lat": 28.5672,
        "lon": 77.2100,
        "phone": "+91 11 2659 3000",
        "has_retina_specialist": True,
        "laser_available": True
    },
    {
        "name": "HV Desai Eye Hospital - Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "lat": 18.5089,
        "lon": 73.9259,
        "phone": "+91 20 2697 0043",
        "has_retina_specialist": True,
        "laser_available": True
    }
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographic coordinates in kilometers."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


class GPSService:
    @staticmethod
    def find_nearest_tertiary_center(phc_lat: float, phc_lon: float) -> dict:
        """
        Finds the closest tertiary eye care hospital with vitreoretinal surgical and laser facilities.
        """
        closest = None
        min_dist = float("inf")

        for center in TERTIARY_EYE_CENTERS:
            dist = haversine_distance_km(phc_lat, phc_lon, center["lat"], center["lon"])
            if dist < min_dist:
                min_dist = dist
                closest = {**center, "distance_km": dist}

        return closest or {
            "name": "District Headquarters Hospital (Eye Dept)",
            "distance_km": 28.5,
            "phone": "108 / 104 National Health Helpline",
            "has_retina_specialist": True
        }
