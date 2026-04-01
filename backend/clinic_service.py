import asyncio
import math
from typing import Dict, List
from urllib.parse import quote_plus

import requests


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def _build_address(tags: Dict[str, str]) -> str:
    parts = [
        tags.get("addr:street"),
        tags.get("addr:city"),
        tags.get("addr:state"),
    ]
    address = ", ".join([part for part in parts if part])
    return address or tags.get("name", "Nearby clinic")


def _fetch_nearby(lat: float, lng: float) -> Dict[str, object]:
    query = f"""
    [out:json][timeout:20];
    (
      node["amenity"~"hospital|clinic|doctors"](around:7000,{lat},{lng});
      way["amenity"~"hospital|clinic|doctors"](around:7000,{lat},{lng});
      relation["amenity"~"hospital|clinic|doctors"](around:7000,{lat},{lng});
    );
    out center tags 15;
    """
    response = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=30)
    response.raise_for_status()
    data = response.json()

    clinics: List[Dict[str, object]] = []
    for index, item in enumerate(data.get("elements", [])):
        item_lat = item.get("lat") or item.get("center", {}).get("lat")
        item_lng = item.get("lon") or item.get("center", {}).get("lon")
        tags = item.get("tags", {})
        if item_lat is None or item_lng is None:
            continue

        name = tags.get("name") or f"Clinic {index + 1}"
        address = _build_address(tags)
        search_query = quote_plus(f"{name} {address}")
        clinics.append(
            {
                "id": str(item.get("id", index + 1)),
                "name": name,
                "address": address,
                "distance_km": round(_haversine_distance(lat, lng, item_lat, item_lng), 1),
                "latitude": item_lat,
                "longitude": item_lng,
                "maps_url": f"https://www.google.com/maps/search/?api=1&query={search_query}",
            }
        )

    clinics.sort(key=lambda clinic: clinic["distance_km"])
    return {
        "map_embed_url": f"https://www.google.com/maps?q={lat},{lng}&z=13&output=embed",
        "emergency_number": "112",
        "clinics": clinics[:8],
    }


def _fallback_response(lat: float, lng: float) -> Dict[str, object]:
    search_url = f"https://www.google.com/maps/search/hospitals/@{lat},{lng},14z"
    return {
        "map_embed_url": f"https://www.google.com/maps?q={lat},{lng}&z=13&output=embed",
        "emergency_number": "112",
        "clinics": [
            {
                "id": "fallback-hospital-search",
                "name": "Nearby hospital search",
                "address": "Open live hospital results centered on your current location.",
                "distance_km": 0.0,
                "latitude": lat,
                "longitude": lng,
                "maps_url": search_url,
            },
            {
                "id": "fallback-clinic-search",
                "name": "Nearby clinic search",
                "address": "Browse nearby clinic options on Google Maps.",
                "distance_km": 0.0,
                "latitude": lat,
                "longitude": lng,
                "maps_url": f"https://www.google.com/maps/search/clinic/@{lat},{lng},14z",
            },
        ],
    }


async def fetch_nearby_clinics(lat: float, lng: float) -> Dict[str, object]:
    try:
        return await asyncio.to_thread(_fetch_nearby, lat, lng)
    except Exception:
        return _fallback_response(lat, lng)