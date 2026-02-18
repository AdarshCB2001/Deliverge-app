#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DelivergeAPITester:
    def __init__(self, base_url: str):
        """Initialize the API tester with the base URL"""
        self.base_url = base_url.rstrip('/')
        self.session_token: Optional[str] = None
        self.user_data: Optional[Dict[str, Any]] = None
        self.delivery_id: Optional[str] = None
        
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_required: bool = False
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if auth is required and token is available
        if auth_required and self.session_token:
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {self.session_token}"
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_time = time.time() - start_time
                    
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                    
                    logger.info(f"{method} {endpoint} - Status: {response.status} - Time: {response_time:.2f}s")
                    
                    return {
                        "status": response.status,
                        "data": response_data,
                        "response_time": response_time,
                        "success": 200 <= response.status < 300
                    }
            except Exception as e:
                response_time = time.time() - start_time
                logger.error(f"{method} {endpoint} - Error: {str(e)} - Time: {response_time:.2f}s")
                return {
                    "status": 0,
                    "data": {"error": str(e)},
                    "response_time": response_time,
                    "success": False
                }

    async def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        logger.info("🔍 Testing Health Check...")
        result = await self.make_request("GET", "/health")
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and data.get("status") == "healthy":
                logger.info("✅ Health check passed")
                return True
            else:
                logger.error(f"❌ Health check failed - unexpected response: {data}")
                return False
        else:
            logger.error(f"❌ Health check failed - Status: {result['status']}")
            return False

    async def test_user_registration(self) -> bool:
        """Test user registration"""
        logger.info("🔍 Testing User Registration...")
        
        user_data = {
            "name": "Arjun Patel",
            "email": "arjun.patel@example.com",
            "password": "SecurePassword123"
        }
        
        result = await self.make_request("POST", "/auth/register", data=user_data)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and "user" in data and "session_token" in data:
                self.session_token = data["session_token"]
                self.user_data = data["user"]
                logger.info("✅ User registration successful")
                logger.info(f"   User ID: {self.user_data.get('user_id')}")
                logger.info(f"   Role: {self.user_data.get('role')}")
                return True
            else:
                logger.error(f"❌ Registration failed - unexpected response: {data}")
                return False
        else:
            logger.error(f"❌ Registration failed - Status: {result['status']}, Data: {result['data']}")
            return False

    async def test_user_login(self) -> bool:
        """Test user login"""
        logger.info("🔍 Testing User Login...")
        
        params = {
            "email": "arjun.patel@example.com",
            "password": "SecurePassword123"
        }
        
        result = await self.make_request("POST", "/auth/login", params=params)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and "user" in data and "session_token" in data:
                # Update session token (in case it's different)
                self.session_token = data["session_token"]
                logger.info("✅ User login successful")
                return True
            else:
                logger.error(f"❌ Login failed - unexpected response: {data}")
                return False
        else:
            logger.error(f"❌ Login failed - Status: {result['status']}, Data: {result['data']}")
            return False

    async def test_get_current_user(self) -> bool:
        """Test getting current user info (protected endpoint)"""
        logger.info("🔍 Testing Get Current User...")
        
        result = await self.make_request("GET", "/auth/me", auth_required=True)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and "user_id" in data:
                logger.info("✅ Get current user successful")
                logger.info(f"   User: {data.get('name')} ({data.get('email')})")
                return True
            else:
                logger.error(f"❌ Get current user failed - unexpected response: {data}")
                return False
        else:
            logger.error(f"❌ Get current user failed - Status: {result['status']}, Data: {result['data']}")
            return False

    async def test_unauthorized_access(self) -> bool:
        """Test that protected endpoints return 401 without token"""
        logger.info("🔍 Testing Unauthorized Access...")
        
        result = await self.make_request("GET", "/auth/me", auth_required=False)
        
        if result["status"] == 401:
            logger.info("✅ Unauthorized access properly blocked")
            return True
        else:
            logger.error(f"❌ Authorization not enforced - Status: {result['status']}")
            return False

    async def test_switch_role_to_carrier(self) -> bool:
        """Test switching role to carrier"""
        logger.info("🔍 Testing Role Switch to Carrier...")
        
        params = {"role": "carrier"}
        result = await self.make_request("PUT", "/users/role", params=params, auth_required=True)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and data.get("role") == "carrier":
                logger.info("✅ Role switch to carrier successful")
                return True
            else:
                logger.error(f"❌ Role switch failed - unexpected response: {data}")
                return False
        else:
            logger.error(f"❌ Role switch failed - Status: {result['status']}, Data: {result['data']}")
            return False

    async def test_create_delivery_request(self) -> bool:
        """Test creating a delivery request"""
        logger.info("🔍 Testing Create Delivery Request...")
        
        delivery_data = {
            "pickup_address": "Panaji, Goa",
            "pickup_lat": 15.4909,
            "pickup_lng": 73.8278,
            "dropoff_address": "Margao, Goa",
            "dropoff_lat": 15.2832,
            "dropoff_lng": 73.9685,
            "parcel_category": "documents",
            "weight_kg": 0.5,
            "declared_value": 100,
            "parcel_photos_base64": ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="],
            "timing_preference": "asap"
        }
        
        result = await self.make_request("POST", "/deliveries", data=delivery_data, auth_required=True)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and "delivery_id" in data and "price_rs" in data:
                self.delivery_id = data["delivery_id"]
                logger.info("✅ Delivery creation successful")
                logger.info(f"   Delivery ID: {data.get('delivery_id')}")
                logger.info(f"   Price: ₹{data.get('price_rs')}")
                logger.info(f"   Distance: {data.get('distance_km')} km")
                return True
            else:
                logger.error(f"❌ Delivery creation failed - unexpected response: {data}")
                return False
        else:
            logger.error(f"❌ Delivery creation failed - Status: {result['status']}, Data: {result['data']}")
            return False

    async def test_get_user_deliveries(self) -> bool:
        """Test getting user deliveries"""
        logger.info("🔍 Testing Get User Deliveries...")
        
        result = await self.make_request("GET", "/deliveries", auth_required=True)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, list):
                logger.info("✅ Get deliveries successful")
                logger.info(f"   Found {len(data)} deliveries")
                if len(data) > 0:
                    logger.info(f"   First delivery ID: {data[0].get('delivery_id')}")
                return True
            else:
                logger.error(f"❌ Get deliveries failed - unexpected response type: {type(data)}")
                return False
        else:
            logger.error(f"❌ Get deliveries failed - Status: {result['status']}, Data: {result['data']}")
            return False

    async def test_pricing_algorithm(self) -> bool:
        """Test the pricing algorithm with various distances and weights"""
        logger.info("🔍 Testing Pricing Algorithm...")
        
        test_cases = [
            # Distance, Weight, Expected behavior
            (0.3, 0.5, "Should use flat ₹20 (under 0.5km)"),
            (0.7, 0.5, "Should use flat ₹25 (0.5-1km)"),
            (1.5, 0.5, "Should use flat ₹30 (1-2km)"),
            (3.0, 0.5, "Should use formula (above 2km)"),
            (1.0, 3.0, "Should apply weight multiplier (2-5kg)")
        ]
        
        all_passed = True
        
        for distance_km, weight_kg, description in test_cases:
            # Calculate expected coordinates based on distance
            # Using a simple approximation (not exact geodesy)
            lat_diff = distance_km / 111.0  # Rough km to degree conversion
            
            delivery_data = {
                "pickup_address": "Test Pickup",
                "pickup_lat": 15.4909,
                "pickup_lng": 73.8278,
                "dropoff_address": "Test Dropoff",
                "dropoff_lat": 15.4909 + lat_diff,
                "dropoff_lng": 73.8278,
                "parcel_category": "documents",
                "weight_kg": weight_kg,
                "declared_value": 100,
                "parcel_photos_base64": ["data:image/png;base64,test"],
                "timing_preference": "asap"
            }
            
            result = await self.make_request("POST", "/deliveries", data=delivery_data, auth_required=True)
            
            if result["success"]:
                data = result["data"]
                price = data.get("price_rs", 0)
                actual_distance = data.get("distance_km", 0)
                
                logger.info(f"   Distance: {actual_distance:.2f}km, Weight: {weight_kg}kg → Price: ₹{price}")
                logger.info(f"   {description}")
                
                # Basic validation
                if distance_km < 0.5 and price < 15:
                    logger.error(f"   ❌ Price too low for short distance: ₹{price}")
                    all_passed = False
                elif distance_km >= 2 and price < 30:
                    logger.error(f"   ❌ Price too low for long distance: ₹{price}")
                    all_passed = False
            else:
                logger.error(f"   ❌ Pricing test failed for {distance_km}km - Status: {result['status']}")
                all_passed = False
        
        if all_passed:
            logger.info("✅ Pricing algorithm tests passed")
        else:
            logger.error("❌ Some pricing algorithm tests failed")
        
        return all_passed

    async def test_get_delivery_by_id(self) -> bool:
        """Test getting delivery by ID (public endpoint)"""
        logger.info("🔍 Testing Get Delivery by ID...")
        
        if not self.delivery_id:
            logger.error("❌ No delivery ID available for testing")
            return False
        
        result = await self.make_request("GET", f"/deliveries/{self.delivery_id}")
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and data.get("delivery_id") == self.delivery_id:
                logger.info("✅ Get delivery by ID successful")
                logger.info(f"   Status: {data.get('status')}")
                return True
            else:
                logger.error(f"❌ Get delivery by ID failed - unexpected response: {data}")
                return False
        else:
            logger.error(f"❌ Get delivery by ID failed - Status: {result['status']}, Data: {result['data']}")
            return False

    async def test_invalid_role_switch(self) -> bool:
        """Test switching to invalid role should fail"""
        logger.info("🔍 Testing Invalid Role Switch...")
        
        params = {"role": "invalid_role"}
        result = await self.make_request("PUT", "/users/role", params=params, auth_required=True)
        
        if result["status"] == 400:
            logger.info("✅ Invalid role properly rejected")
            return True
        else:
            logger.error(f"❌ Invalid role not rejected - Status: {result['status']}")
            return False

    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all API tests and return results"""
        logger.info("🚀 Starting DELIVERGE API Testing...")
        logger.info(f"Base URL: {self.base_url}")
        
        results = {}
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Current User", self.test_get_current_user),
            ("Unauthorized Access", self.test_unauthorized_access),
            ("Switch Role to Carrier", self.test_switch_role_to_carrier),
            ("Create Delivery Request", self.test_create_delivery_request),
            ("Get User Deliveries", self.test_get_user_deliveries),
            ("Pricing Algorithm", self.test_pricing_algorithm),
            ("Get Delivery by ID", self.test_get_delivery_by_id),
            ("Invalid Role Switch", self.test_invalid_role_switch),
        ]
        
        for test_name, test_func in tests:
            try:
                results[test_name] = await test_func()
            except Exception as e:
                logger.error(f"❌ {test_name} - Exception: {str(e)}")
                results[test_name] = False
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        return results

    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 TEST SUMMARY")
        logger.info("="*60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASSED" if passed_test else "❌ FAILED"
            logger.info(f"{status:<12} {test_name}")
        
        logger.info("-"*60)
        logger.info(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("🎉 All tests passed!")
        else:
            logger.info(f"⚠️  {total - passed} tests failed")


async def main():
    """Main function to run the tests"""
    # API base URL from the review request
    api_base_url = "https://deliverge-pilot.preview.emergentagent.com/api"
    
    tester = DelivergeAPITester(api_base_url)
    results = await tester.run_all_tests()
    tester.print_summary(results)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())