#!/usr/bin/env python3
"""
Backend API Testing for ArogyaAI - Nearby Clinics Feature
Tests the nearby hospitals/clinics API endpoint functionality
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8001"
DEMO_EMAIL = "demo@arogyaai.app"
DEMO_PASSWORD = "Arogya123!"

# Test coordinates (Delhi, India)
TEST_LAT = 28.6139
TEST_LNG = 77.2090

class ClinicAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        
    def test_backend_health(self) -> bool:
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            print(f"✅ Backend Health Check: {response.status_code}")
            print(f"   Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Backend Health Check Failed: {e}")
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication with demo credentials"""
        try:
            # Test login endpoint
            login_data = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
            print(f"✅ Login Test: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                print(f"   Token received: {auth_data.get('token', 'N/A')[:20]}...")
                print(f"   User: {auth_data.get('user', {}).get('email', 'N/A')}")
                
                # Check if access_token cookie is set
                cookies = response.cookies
                if 'access_token' in cookies:
                    self.access_token = cookies['access_token']
                    print(f"   Access token cookie set: {self.access_token[:20]}...")
                    return True
                else:
                    print("   ⚠️  No access_token cookie found")
                    return False
            else:
                print(f"   ❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication Test Failed: {e}")
            return False
    
    def test_auth_verification(self) -> bool:
        """Test if authentication token works"""
        try:
            response = self.session.get(f"{BACKEND_URL}/api/auth/me")
            print(f"✅ Auth Verification: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   Authenticated user: {user_data.get('email', 'N/A')}")
                return True
            else:
                print(f"   ❌ Auth verification failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Auth Verification Failed: {e}")
            return False
    
    def test_nearby_clinics_api(self) -> Dict[str, Any]:
        """Test the nearby clinics API endpoint"""
        try:
            # Test the API endpoint
            params = {
                "lat": TEST_LAT,
                "lng": TEST_LNG
            }
            
            print(f"🏥 Testing Nearby Clinics API with coordinates: {TEST_LAT}, {TEST_LNG}")
            start_time = time.time()
            
            response = self.session.get(f"{BACKEND_URL}/api/clinics/nearby", params=params)
            end_time = time.time()
            
            print(f"✅ Nearby Clinics API: {response.status_code} (took {end_time - start_time:.2f}s)")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["map_embed_url", "emergency_number", "clinics"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    return {"success": False, "error": f"Missing fields: {missing_fields}"}
                
                # Validate map_embed_url
                map_url = data.get("map_embed_url", "")
                if not map_url.startswith("https://www.google.com/maps"):
                    print(f"   ❌ Invalid map_embed_url format: {map_url}")
                    return {"success": False, "error": "Invalid map_embed_url format"}
                
                # Validate emergency_number
                emergency_num = data.get("emergency_number", "")
                if not emergency_num:
                    print(f"   ❌ Missing emergency_number")
                    return {"success": False, "error": "Missing emergency_number"}
                
                # Validate clinics array
                clinics = data.get("clinics", [])
                print(f"   📍 Found {len(clinics)} clinics")
                
                if len(clinics) == 0:
                    print("   ⚠️  No clinics found - this might be expected for some locations")
                
                # Validate clinic structure
                for i, clinic in enumerate(clinics[:3]):  # Check first 3 clinics
                    required_clinic_fields = ["id", "name", "address", "distance_km", "latitude", "longitude", "maps_url"]
                    missing_clinic_fields = [field for field in required_clinic_fields if field not in clinic]
                    
                    if missing_clinic_fields:
                        print(f"   ❌ Clinic {i+1} missing fields: {missing_clinic_fields}")
                        return {"success": False, "error": f"Clinic {i+1} missing fields: {missing_clinic_fields}"}
                    
                    print(f"   🏥 Clinic {i+1}: {clinic['name']} ({clinic['distance_km']}km)")
                    print(f"      Address: {clinic['address']}")
                    print(f"      Maps URL: {clinic['maps_url'][:60]}...")
                
                print(f"   ✅ Response structure is valid")
                print(f"   🗺️  Map URL: {map_url}")
                print(f"   🚨 Emergency Number: {emergency_num}")
                
                return {
                    "success": True, 
                    "data": data,
                    "clinic_count": len(clinics),
                    "response_time": end_time - start_time
                }
                
            elif response.status_code == 401:
                print(f"   ❌ Authentication required: {response.text}")
                return {"success": False, "error": "Authentication failed"}
            else:
                print(f"   ❌ API call failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ Nearby Clinics API Test Failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_openstreetmap_integration(self) -> bool:
        """Test if OpenStreetMap Overpass API is accessible"""
        try:
            print("🌍 Testing OpenStreetMap Overpass API integration...")
            
            # Simple test query to check if Overpass API is accessible
            test_query = """
            [out:json][timeout:10];
            node["amenity"="hospital"](around:1000,28.6139,77.2090);
            out 1;
            """
            
            response = requests.post(
                "https://overpass-api.de/api/interpreter", 
                data=test_query, 
                timeout=15
            )
            
            print(f"✅ OpenStreetMap API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                print(f"   📍 Test query returned {len(elements)} elements")
                return True
            else:
                print(f"   ❌ OpenStreetMap API failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ OpenStreetMap Integration Test Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("=" * 60)
        print("🧪 AROGYAAI BACKEND API TESTING - NEARBY CLINICS FEATURE")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Backend Health
        results["backend_health"] = self.test_backend_health()
        print()
        
        # Test 2: Authentication
        results["authentication"] = self.test_authentication()
        print()
        
        # Test 3: Auth Verification
        if results["authentication"]:
            results["auth_verification"] = self.test_auth_verification()
        else:
            results["auth_verification"] = False
            print("⏭️  Skipping auth verification (login failed)")
        print()
        
        # Test 4: OpenStreetMap Integration
        results["openstreetmap"] = self.test_openstreetmap_integration()
        print()
        
        # Test 5: Nearby Clinics API
        if results["auth_verification"]:
            clinic_result = self.test_nearby_clinics_api()
            results["nearby_clinics"] = clinic_result["success"]
            results["clinic_details"] = clinic_result
        else:
            results["nearby_clinics"] = False
            print("⏭️  Skipping nearby clinics API (authentication failed)")
        
        print()
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            if test_name == "clinic_details":
                continue
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Overall assessment
        critical_tests = ["backend_health", "authentication", "auth_verification", "nearby_clinics"]
        critical_passed = sum(1 for test in critical_tests if results.get(test, False))
        
        print()
        if critical_passed == len(critical_tests):
            print("🎉 ALL CRITICAL TESTS PASSED - Nearby Clinics API is working correctly!")
        else:
            print(f"⚠️  {critical_passed}/{len(critical_tests)} critical tests passed")
            print("🔧 Issues found that need attention:")
            for test in critical_tests:
                if not results.get(test, False):
                    print(f"   - {test.replace('_', ' ').title()}")
        
        return results

if __name__ == "__main__":
    tester = ClinicAPITester()
    results = tester.run_all_tests()