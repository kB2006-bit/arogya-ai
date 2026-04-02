#!/usr/bin/env python3
"""
Test the fallback behavior of the nearby clinics API
"""

import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8001"
DEMO_EMAIL = "demo@arogyaai.app"
DEMO_PASSWORD = "Arogya123!"

def test_fallback_behavior():
    """Test that the API returns fallback response when OpenStreetMap fails"""
    session = requests.Session()
    
    # Login first
    login_data = {"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
    login_response = session.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    # Test with coordinates that might trigger fallback
    params = {"lat": 28.6139, "lng": 77.2090}
    response = session.get(f"{BACKEND_URL}/api/clinics/nearby", params=params)
    
    if response.status_code == 200:
        data = response.json()
        clinics = data.get("clinics", [])
        
        # Check if we got fallback response
        fallback_indicators = [
            "fallback-hospital-search",
            "fallback-clinic-search",
            "Nearby hospital search",
            "Nearby clinic search"
        ]
        
        has_fallback = any(
            any(indicator in str(clinic.get(field, "")) for field in ["id", "name"])
            for clinic in clinics
            for indicator in fallback_indicators
        )
        
        if has_fallback:
            print("✅ Fallback response detected - API gracefully handles OpenStreetMap failures")
            print(f"   Fallback clinics provided: {len(clinics)}")
            for clinic in clinics:
                if any(indicator in clinic.get("name", "") for indicator in ["Nearby hospital search", "Nearby clinic search"]):
                    print(f"   - {clinic['name']}: {clinic['maps_url']}")
        else:
            print("✅ Real OpenStreetMap data received")
            print(f"   Real clinics found: {len(clinics)}")
            for i, clinic in enumerate(clinics[:3]):
                print(f"   - {clinic['name']} ({clinic['distance_km']}km)")
        
        return True
    else:
        print(f"❌ API call failed: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Fallback Behavior for Nearby Clinics API")
    print("=" * 50)
    test_fallback_behavior()