#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging
import time
import base64
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveDelivergeAPITester:
    def __init__(self, base_url: str):
        """Initialize the comprehensive API tester with the base URL"""
        self.base_url = base_url.rstrip('/')
        
        # User session management
        self.sender_token: Optional[str] = None
        self.carrier_token: Optional[str] = None
        self.admin_token: Optional[str] = None
        
        # Test data storage
        self.sender_data: Optional[Dict[str, Any]] = None
        self.carrier_data: Optional[Dict[str, Any]] = None
        self.delivery_id: Optional[str] = None
        self.pickup_otp: Optional[str] = None
        self.delivery_otp: Optional[str] = None
        
        # Test counters
        self.test_results = {}
        self.failed_tests = []
        
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token is provided
        if auth_token:
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {auth_token}"
        
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

    def record_test(self, test_name: str, success: bool, details: str = ""):
        """Record test result"""
        self.test_results[test_name] = success
        if not success:
            self.failed_tests.append(f"{test_name}: {details}")
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}")

    # ============================================
    # 1. AUTHENTICATION & USER MANAGEMENT TESTS
    # ============================================

    async def test_auth_and_user_management(self) -> bool:
        """Test all authentication and user management endpoints"""
        logger.info("🔐 Testing Authentication & User Management...")
        
        all_passed = True
        
        # 1.1 Register sender user
        logger.info("📝 Testing user registration...")
        sender_data = {
            "name": "Raj Sharma",
            "email": "raj.sharma.goa@example.com", 
            "password": "SecurePassword123!"
        }
        
        result = await self.make_request("POST", "/auth/register", data=sender_data)
        if result["success"] and "session_token" in result["data"]:
            self.sender_token = result["data"]["session_token"]
            self.sender_data = result["data"]["user"]
            self.record_test("Auth - User Registration", True)
        else:
            self.record_test("Auth - User Registration", False, f"Status: {result['status']}")
            all_passed = False

        # 1.2 Login with registered user
        logger.info("🔑 Testing user login...")
        login_params = {
            "email": "raj.sharma.goa@example.com",
            "password": "SecurePassword123!"
        }
        
        result = await self.make_request("POST", "/auth/login", params=login_params)
        if result["success"]:
            self.record_test("Auth - User Login", True)
        else:
            self.record_test("Auth - User Login", False, f"Status: {result['status']}")
            all_passed = False

        # 1.3 Get current user
        logger.info("👤 Testing get current user...")
        result = await self.make_request("GET", "/auth/me", auth_token=self.sender_token)
        if result["success"]:
            self.record_test("Auth - Get Current User", True)
        else:
            self.record_test("Auth - Get Current User", False, f"Status: {result['status']}")
            all_passed = False

        # 1.4 Test unauthorized access
        logger.info("🚫 Testing unauthorized access...")
        result = await self.make_request("GET", "/auth/me")  # No token
        if result["status"] == 401:
            self.record_test("Auth - Unauthorized Access Blocked", True)
        else:
            self.record_test("Auth - Unauthorized Access Blocked", False, f"Expected 401, got {result['status']}")
            all_passed = False

        # 1.5 Switch to carrier role
        logger.info("🔄 Testing role switch to carrier...")
        params = {"role": "carrier"}
        result = await self.make_request("PUT", "/users/role", params=params, auth_token=self.sender_token)
        if result["success"]:
            self.record_test("User - Role Switch to Carrier", True)
        else:
            self.record_test("User - Role Switch to Carrier", False, f"Status: {result['status']}")
            all_passed = False

        # 1.6 Update profile
        logger.info("📝 Testing profile update...")
        params = {
            "name": "Raj Sharma Updated",
            "phone_whatsapp": "+91-9876543210"
        }
        result = await self.make_request("PUT", "/users/profile", params=params, auth_token=self.sender_token)
        if result["success"]:
            self.record_test("User - Profile Update", True)
        else:
            self.record_test("User - Profile Update", False, f"Status: {result['status']}")
            all_passed = False

        # 1.7 Test logout
        logger.info("🚪 Testing logout...")
        result = await self.make_request("POST", "/auth/logout", auth_token=self.sender_token)
        if result["success"]:
            self.record_test("Auth - Logout", True)
        else:
            self.record_test("Auth - Logout", False, f"Status: {result['status']}")
            all_passed = False

        return all_passed

    # ============================================
    # 2. CARRIER PROFILE & KYC TESTS
    # ============================================

    async def test_carrier_kyc_system(self) -> bool:
        """Test carrier profile and KYC system"""
        logger.info("🚗 Testing Carrier Profile & KYC System...")
        
        all_passed = True
        
        # Create a fresh carrier user for testing
        logger.info("📝 Creating carrier user...")
        carrier_data = {
            "name": "Priya Desai",
            "email": "priya.desai.carrier@example.com",
            "password": "CarrierPassword123!"
        }
        
        result = await self.make_request("POST", "/auth/register", data=carrier_data)
        if result["success"]:
            self.carrier_token = result["data"]["session_token"]
            self.carrier_data = result["data"]["user"]
            self.record_test("Carrier - User Creation", True)
        else:
            self.record_test("Carrier - User Creation", False, f"Status: {result['status']}")
            return False

        # Switch to carrier role
        params = {"role": "carrier"}
        await self.make_request("PUT", "/users/role", params=params, auth_token=self.carrier_token)

        # 2.1 Submit KYC with mock base64 images
        logger.info("📋 Testing KYC submission...")
        
        # Create mock base64 images (1x1 pixel PNG)
        mock_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        kyc_data = {
            "phone_whatsapp": "+91-9876543211",
            "vehicle_type": "bike",
            "aadhaar_photo_base64": mock_image,
            "selfie_photo_base64": mock_image
        }
        
        result = await self.make_request("POST", "/carrier/kyc", data=kyc_data, auth_token=self.carrier_token)
        if result["success"] and result["data"].get("status") == "pending":
            self.record_test("Carrier - KYC Submission", True)
        else:
            self.record_test("Carrier - KYC Submission", False, f"Status: {result['status']}")
            all_passed = False

        # 2.2 Get carrier profile
        logger.info("👤 Testing get carrier profile...")
        result = await self.make_request("GET", "/carrier/profile", auth_token=self.carrier_token)
        if result["success"]:
            self.record_test("Carrier - Get Profile", True)
        else:
            self.record_test("Carrier - Get Profile", False, f"Status: {result['status']}")
            all_passed = False

        # 2.3 Try to go online (should fail - KYC not approved)
        logger.info("🔴 Testing online toggle without approval...")
        params = {"is_online": True}
        result = await self.make_request("PUT", "/carrier/online", params=params, auth_token=self.carrier_token)
        if result["status"] == 403:  # Should be forbidden
            self.record_test("Carrier - Online Status Blocked (Pre-approval)", True)
        else:
            self.record_test("Carrier - Online Status Blocked (Pre-approval)", False, f"Expected 403, got {result['status']}")
            all_passed = False

        return all_passed

    # ============================================
    # 3. DELIVERY MANAGEMENT TESTS
    # ============================================

    async def test_delivery_management(self) -> bool:
        """Test comprehensive delivery management"""
        logger.info("📦 Testing Delivery Management System...")
        
        all_passed = True
        
        # Ensure we have a sender token
        if not self.sender_token:
            # Re-login as sender
            login_params = {
                "email": "raj.sharma.goa@example.com",
                "password": "SecurePassword123!"
            }
            result = await self.make_request("POST", "/auth/login", params=login_params)
            if result["success"]:
                self.sender_token = result["data"]["session_token"]

        # Switch back to sender role
        params = {"role": "sender"}
        await self.make_request("PUT", "/users/role", params=params, auth_token=self.sender_token)

        # 3.1 Create delivery (Panaji to Margao)
        logger.info("📦 Testing delivery creation (Panaji → Margao)...")
        
        delivery_data = {
            "pickup_address": "Panaji Market, Panaji, Goa 403001",
            "pickup_lat": 15.4909,
            "pickup_lng": 73.8278,
            "dropoff_address": "Margao Railway Station, Margao, Goa 403601",
            "dropoff_lat": 15.2832,
            "dropoff_lng": 73.9685,
            "parcel_category": "documents",
            "weight_kg": 0.5,
            "declared_value": 500,
            "parcel_photos_base64": ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="],
            "timing_preference": "asap"
        }
        
        result = await self.make_request("POST", "/deliveries", data=delivery_data, auth_token=self.sender_token)
        if result["success"] and "delivery_id" in result["data"]:
            self.delivery_id = result["data"]["delivery_id"]
            price = result["data"].get("price_rs", 0)
            distance = result["data"].get("distance_km", 0)
            logger.info(f"   Created delivery: {self.delivery_id}")
            logger.info(f"   Price: ₹{price}, Distance: {distance:.2f}km")
            self.record_test("Delivery - Creation (Panaji→Margao)", True)
        else:
            self.record_test("Delivery - Creation (Panaji→Margao)", False, f"Status: {result['status']}")
            all_passed = False

        # 3.2 Get user deliveries
        logger.info("📋 Testing get user deliveries...")
        result = await self.make_request("GET", "/deliveries", auth_token=self.sender_token)
        if result["success"] and isinstance(result["data"], list):
            self.record_test("Delivery - Get User Deliveries", True)
            logger.info(f"   Found {len(result['data'])} deliveries")
        else:
            self.record_test("Delivery - Get User Deliveries", False, f"Status: {result['status']}")
            all_passed = False

        # 3.3 Get nearby deliveries (as carrier)
        logger.info("🗺️ Testing get nearby deliveries...")
        params = {
            "lat": 15.49,
            "lng": 73.82,
            "max_distance_km": 50
        }
        result = await self.make_request("GET", "/deliveries/nearby", params=params, auth_token=self.carrier_token)
        if result["status"] == 403:  # Expected - KYC not approved
            self.record_test("Delivery - Nearby (KYC Protection)", True)
        else:
            self.record_test("Delivery - Nearby (KYC Protection)", False, f"Expected 403, got {result['status']}")
            all_passed = False

        # 3.4 Get single delivery (public endpoint)
        if self.delivery_id:
            logger.info("🔍 Testing get single delivery...")
            result = await self.make_request("GET", f"/deliveries/{self.delivery_id}")
            if result["success"]:
                self.record_test("Delivery - Get Single Delivery", True)
            else:
                self.record_test("Delivery - Get Single Delivery", False, f"Status: {result['status']}")
                all_passed = False

        return all_passed

    # ============================================
    # 4. PRICING ALGORITHM TESTS
    # ============================================

    async def test_pricing_algorithm(self) -> bool:
        """Test pricing algorithm with different scenarios"""
        logger.info("💰 Testing Pricing Algorithm...")
        
        all_passed = True
        
        test_cases = [
            # (distance_km, weight_kg, expected_behavior, min_price)
            (0.3, 0.5, "Under 0.5km → Should be ₹20", 20),
            (0.7, 0.5, "0.5-1km → Should be ₹25", 25),
            (1.5, 0.5, "1-2km → Should be ₹30", 30),
            (33, 0.5, "33km (Panaji-Margao) → Should be ~₹157", 150),
            (1.0, 3.0, "Weight 2-5kg → Should apply multiplier", 30)
        ]
        
        for i, (distance_km, weight_kg, description, min_expected) in enumerate(test_cases):
            logger.info(f"💰 Testing pricing case {i+1}: {description}")
            
            # Calculate coordinates based on distance (rough approximation)
            lat_diff = distance_km / 111.0  # Rough km to degree conversion
            
            delivery_data = {
                "pickup_address": f"Test Pickup {i+1}",
                "pickup_lat": 15.4909,
                "pickup_lng": 73.8278,
                "dropoff_address": f"Test Dropoff {i+1}",
                "dropoff_lat": 15.4909 + lat_diff,
                "dropoff_lng": 73.8278,
                "parcel_category": "documents",
                "weight_kg": weight_kg,
                "declared_value": 100,
                "parcel_photos_base64": ["data:image/png;base64,test"],
                "timing_preference": "asap"
            }
            
            result = await self.make_request("POST", "/deliveries", data=delivery_data, auth_token=self.sender_token)
            
            if result["success"]:
                price = result["data"].get("price_rs", 0)
                actual_distance = result["data"].get("distance_km", 0)
                
                logger.info(f"   Distance: {actual_distance:.2f}km, Weight: {weight_kg}kg → Price: ₹{price}")
                
                # Validate pricing
                if price >= min_expected:
                    self.record_test(f"Pricing - Case {i+1}", True)
                else:
                    self.record_test(f"Pricing - Case {i+1}", False, f"Price ₹{price} < expected ₹{min_expected}")
                    all_passed = False
            else:
                self.record_test(f"Pricing - Case {i+1}", False, f"Request failed: {result['status']}")
                all_passed = False
        
        return all_passed

    # ============================================
    # 5. ADMIN ENDPOINTS TESTS
    # ============================================

    async def test_admin_endpoints(self) -> bool:
        """Test admin-only endpoints"""
        logger.info("👑 Testing Admin Endpoints...")
        
        all_passed = True
        
        # Create admin user (in real app, this would be done via database)
        # For testing, we'll use regular user and see if admin endpoints are protected
        
        # 5.1 Test KYC pending (should fail - not admin)
        logger.info("📋 Testing get pending KYC (should fail)...")
        result = await self.make_request("GET", "/admin/kyc/pending", auth_token=self.sender_token)
        if result["status"] == 403:
            self.record_test("Admin - KYC Pending Access Denied", True)
        else:
            self.record_test("Admin - KYC Pending Access Denied", False, f"Expected 403, got {result['status']}")
            all_passed = False

        # 5.2 Test KYC approval (should fail - not admin)
        logger.info("✅ Testing KYC approval (should fail)...")
        if self.carrier_data:
            user_id = self.carrier_data["user_id"]
            result = await self.make_request("PUT", f"/admin/kyc/{user_id}/approve", auth_token=self.sender_token)
            if result["status"] == 403:
                self.record_test("Admin - KYC Approval Access Denied", True)
            else:
                self.record_test("Admin - KYC Approval Access Denied", False, f"Expected 403, got {result['status']}")
                all_passed = False

        # 5.3 Test get config (should fail - not admin)
        logger.info("⚙️ Testing get config (should fail)...")
        result = await self.make_request("GET", "/admin/config", auth_token=self.sender_token)
        if result["status"] == 403:
            self.record_test("Admin - Config Access Denied", True)
        else:
            self.record_test("Admin - Config Access Denied", False, f"Expected 403, got {result['status']}")
            all_passed = False

        # 5.4 Test update config (should fail - not admin)
        logger.info("⚙️ Testing update config (should fail)...")
        params = {"key": "base_fare", "value": 30}
        result = await self.make_request("PUT", "/admin/config", params=params, auth_token=self.sender_token)
        if result["status"] == 403:
            self.record_test("Admin - Config Update Access Denied", True)
        else:
            self.record_test("Admin - Config Update Access Denied", False, f"Expected 403, got {result['status']}")
            all_passed = False

        return all_passed

    # ============================================
    # 6. OTP SYSTEM TESTS
    # ============================================

    async def test_otp_system(self) -> bool:
        """Test OTP system functionality"""
        logger.info("🔐 Testing OTP System...")
        
        all_passed = True
        
        # For OTP testing, we need to simulate a complete flow
        # But since we can't approve KYC without admin access, we'll test what we can
        
        # 6.1 Test delivery acceptance (should fail - carrier not approved)
        if self.delivery_id and self.carrier_token:
            logger.info("📦 Testing delivery acceptance (should fail)...")
            result = await self.make_request("PUT", f"/deliveries/{self.delivery_id}/accept", auth_token=self.carrier_token)
            
            # This might succeed if the acceptance doesn't check KYC status
            if result["success"]:
                if "pickup_otp" in result["data"] and "delivery_otp" in result["data"]:
                    self.pickup_otp = result["data"]["pickup_otp"]
                    self.delivery_otp = result["data"]["delivery_otp"]
                    self.record_test("OTP - Delivery Acceptance & OTP Generation", True)
                    logger.info(f"   Generated OTPs: Pickup={self.pickup_otp}, Delivery={self.delivery_otp}")
                    
                    # 6.2 Test OTP verification
                    logger.info("🔐 Testing OTP verification...")
                    
                    # Test pickup OTP
                    otp_data = {
                        "delivery_id": self.delivery_id,
                        "otp": self.pickup_otp,
                        "otp_type": "pickup"
                    }
                    
                    result = await self.make_request("POST", f"/deliveries/{self.delivery_id}/verify-otp", data=otp_data, auth_token=self.carrier_token)
                    if result["success"]:
                        self.record_test("OTP - Pickup Verification", True)
                        
                        # Test delivery OTP
                        otp_data["otp"] = self.delivery_otp
                        otp_data["otp_type"] = "delivery"
                        
                        result = await self.make_request("POST", f"/deliveries/{self.delivery_id}/verify-otp", data=otp_data, auth_token=self.carrier_token)
                        if result["success"]:
                            self.record_test("OTP - Delivery Verification", True)
                        else:
                            self.record_test("OTP - Delivery Verification", False, f"Status: {result['status']}")
                            all_passed = False
                    else:
                        self.record_test("OTP - Pickup Verification", False, f"Status: {result['status']}")
                        all_passed = False
                        
                else:
                    self.record_test("OTP - Delivery Acceptance & OTP Generation", False, "No OTPs in response")
                    all_passed = False
            else:
                self.record_test("OTP - Delivery Acceptance", False, f"Status: {result['status']}")
                # This might be expected behavior
                logger.info("   (This might be expected if KYC approval is required)")

        # 6.3 Test invalid OTP
        if self.delivery_id:
            logger.info("❌ Testing invalid OTP...")
            otp_data = {
                "delivery_id": self.delivery_id,
                "otp": "9999",  # Invalid OTP
                "otp_type": "pickup"
            }
            
            result = await self.make_request("POST", f"/deliveries/{self.delivery_id}/verify-otp", data=otp_data, auth_token=self.carrier_token)
            if result["status"] == 401:  # Should be unauthorized
                self.record_test("OTP - Invalid OTP Rejected", True)
            else:
                self.record_test("OTP - Invalid OTP Rejected", False, f"Expected 401, got {result['status']}")
                all_passed = False
        
        return all_passed

    # ============================================
    # 7. CHAT & LOCATION TESTS
    # ============================================

    async def test_chat_and_location(self) -> bool:
        """Test chat and location tracking"""
        logger.info("💬 Testing Chat & Location Tracking...")
        
        all_passed = True
        
        if not self.delivery_id:
            logger.info("⚠️ No delivery ID available for chat/location tests")
            return False

        # 7.1 Test sending message
        logger.info("💬 Testing send message...")
        message_data = {
            "delivery_id": self.delivery_id,
            "content": "Hello! I'm ready to pick up the parcel."
        }
        
        result = await self.make_request("POST", "/messages", data=message_data, auth_token=self.carrier_token)
        if result["success"]:
            self.record_test("Chat - Send Message", True)
        else:
            self.record_test("Chat - Send Message", False, f"Status: {result['status']}")
            all_passed = False

        # 7.2 Test getting messages
        logger.info("📬 Testing get messages...")
        result = await self.make_request("GET", f"/messages/{self.delivery_id}", auth_token=self.carrier_token)
        if result["success"]:
            self.record_test("Chat - Get Messages", True)
        else:
            self.record_test("Chat - Get Messages", False, f"Status: {result['status']}")
            all_passed = False

        # 7.3 Test location update
        logger.info("📍 Testing location update...")
        params = {
            "lat": 15.4909,
            "lng": 73.8278
        }
        result = await self.make_request("POST", f"/deliveries/{self.delivery_id}/location", params=params, auth_token=self.carrier_token)
        if result["success"]:
            self.record_test("Location - Update GPS", True)
        else:
            self.record_test("Location - Update GPS", False, f"Status: {result['status']}")
            all_passed = False

        # 7.4 Test get location history
        logger.info("🗺️ Testing get location history...")
        result = await self.make_request("GET", f"/deliveries/{self.delivery_id}/locations")
        if result["success"]:
            self.record_test("Location - Get History", True)
        else:
            self.record_test("Location - Get History", False, f"Status: {result['status']}")
            all_passed = False

        # 7.5 Test get user ratings
        logger.info("⭐ Testing get user ratings...")
        result = await self.make_request("GET", "/ratings/me", auth_token=self.carrier_token)
        if result["success"]:
            self.record_test("Ratings - Get User Ratings", True)
        else:
            self.record_test("Ratings - Get User Ratings", False, f"Status: {result['status']}")
            all_passed = False

        return all_passed

    # ============================================
    # 8. PERFORMANCE & DATA INTEGRITY TESTS
    # ============================================

    async def test_performance_and_integrity(self) -> bool:
        """Test performance metrics and data integrity"""
        logger.info("⚡ Testing Performance & Data Integrity...")
        
        all_passed = True
        
        # 8.1 Health check performance
        logger.info("💓 Testing health check performance...")
        start_time = time.time()
        result = await self.make_request("GET", "/health")
        response_time = time.time() - start_time
        
        if result["success"] and response_time < 1.0:  # Should respond within 1 second
            self.record_test("Performance - Health Check Speed", True)
        else:
            self.record_test("Performance - Health Check Speed", False, f"Took {response_time:.2f}s")
            all_passed = False

        # 8.2 Data consistency check
        logger.info("🔍 Testing data consistency...")
        if self.delivery_id:
            # Get delivery via different endpoints and compare
            result1 = await self.make_request("GET", f"/deliveries/{self.delivery_id}")
            result2 = await self.make_request("GET", "/deliveries", auth_token=self.sender_token)
            
            if result1["success"] and result2["success"]:
                delivery_public = result1["data"]
                deliveries_list = result2["data"]
                
                # Find our delivery in the list
                delivery_private = None
                for d in deliveries_list:
                    if d["delivery_id"] == self.delivery_id:
                        delivery_private = d
                        break
                
                if delivery_private and delivery_public["delivery_id"] == delivery_private["delivery_id"]:
                    self.record_test("Data - Consistency Check", True)
                else:
                    self.record_test("Data - Consistency Check", False, "Data mismatch between endpoints")
                    all_passed = False
            else:
                self.record_test("Data - Consistency Check", False, "Failed to fetch data for comparison")
                all_passed = False

        return all_passed

    # ============================================
    # MAIN TEST RUNNER
    # ============================================

    async def run_comprehensive_tests(self) -> Dict[str, bool]:
        """Run all comprehensive API tests"""
        logger.info("🚀 Starting Comprehensive DELIVERGE API Testing...")
        logger.info(f"Base URL: {self.base_url}")
        logger.info("="*80)
        
        test_suites = [
            ("1. Authentication & User Management", self.test_auth_and_user_management),
            ("2. Carrier Profile & KYC", self.test_carrier_kyc_system),
            ("3. Delivery Management", self.test_delivery_management),
            ("4. Pricing Algorithm", self.test_pricing_algorithm),
            ("5. Admin Endpoints", self.test_admin_endpoints),
            ("6. OTP System", self.test_otp_system),
            ("7. Chat & Location", self.test_chat_and_location),
            ("8. Performance & Integrity", self.test_performance_and_integrity),
        ]
        
        for suite_name, test_func in test_suites:
            logger.info(f"\n📋 {suite_name}")
            logger.info("-" * 60)
            
            try:
                await test_func()
            except Exception as e:
                logger.error(f"❌ Test suite failed with exception: {str(e)}")
                self.record_test(f"{suite_name} - Exception", False, str(e))
            
            # Small delay between test suites
            await asyncio.sleep(1)
        
        return self.test_results

    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        logger.info("\n" + "="*80)
        logger.info("📊 COMPREHENSIVE TEST SUMMARY")
        logger.info("="*80)
        
        passed = sum(self.test_results.values())
        total = len(self.test_results)
        
        # Group results by category
        categories = {}
        for test_name, result in self.test_results.items():
            category = test_name.split(" - ")[0] if " - " in test_name else "General"
            if category not in categories:
                categories[category] = {"passed": 0, "total": 0}
            categories[category]["total"] += 1
            if result:
                categories[category]["passed"] += 1
        
        # Print by category
        for category, stats in categories.items():
            logger.info(f"\n{category}:")
            logger.info(f"  {stats['passed']}/{stats['total']} tests passed ({stats['passed']/stats['total']*100:.1f}%)")
        
        # Print individual test results
        logger.info(f"\nDetailed Results:")
        for test_name, passed_test in self.test_results.items():
            status = "✅ PASSED" if passed_test else "❌ FAILED"
            logger.info(f"  {status:<12} {test_name}")
        
        # Print failures
        if self.failed_tests:
            logger.info(f"\n❌ Failed Tests Details:")
            for failure in self.failed_tests:
                logger.info(f"  • {failure}")
        
        logger.info("-"*80)
        logger.info(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("🎉 All tests passed! API is fully functional.")
        elif passed / total >= 0.8:
            logger.info("✅ Most tests passed. API is largely functional with minor issues.")
        else:
            logger.info("⚠️ Significant issues found. API needs attention.")


async def main():
    """Main function to run comprehensive tests"""
    # API base URL from the review request
    api_base_url = "https://deliverge-pilot.preview.emergentagent.com/api"
    
    tester = ComprehensiveDelivergeAPITester(api_base_url)
    results = await tester.run_comprehensive_tests()
    tester.print_comprehensive_summary()
    
    return results


if __name__ == "__main__":
    asyncio.run(main())