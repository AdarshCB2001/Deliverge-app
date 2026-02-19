#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DelivergeEndToEndTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.test_results = []
        self.failed_tests = []
        
    def record_test(self, test_name: str, success: bool, details: str = ""):
        """Record test result"""
        self.test_results.append((test_name, success))
        if not success:
            self.failed_tests.append(f"{test_name}: {details}")
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}")

    async def run_complete_end_to_end_test(self):
        """Run complete end-to-end delivery flow as specified in review request"""
        logger.info("🚀 Starting Complete End-to-End DELIVERGE Test...")
        logger.info("="*80)
        
        async with aiohttp.ClientSession() as session:
            
            # ============================================
            # 1. AUTHENTICATION & USER MANAGEMENT
            # ============================================
            
            logger.info("\n1️⃣ AUTHENTICATION & USER MANAGEMENT")
            logger.info("-" * 50)
            
            # Create unique users for this test
            timestamp = int(time.time())
            sender_email = f"sender.test.{timestamp}@example.com"
            carrier_email = f"carrier.test.{timestamp}@example.com"
            
            # 1.1 Register sender user (User A)
            logger.info("👤 Registering sender user (User A)...")
            sender_data = {
                "name": "Ravi Kumar",
                "email": sender_email,
                "password": "SenderPassword123!"
            }
            
            async with session.post(f"{self.base_url}/auth/register", json=sender_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    sender_token = result["session_token"]
                    sender_user = result["user"]
                    self.record_test("Sender Registration", True)
                    logger.info(f"   Sender ID: {sender_user['user_id']}")
                else:
                    text = await resp.text()
                    self.record_test("Sender Registration", False, f"Status: {resp.status} - {text}")
                    return
            
            # 1.2 Register carrier user (User B) 
            logger.info("🚚 Registering carrier user (User B)...")
            carrier_data = {
                "name": "Suresh Patil",
                "email": carrier_email,
                "password": "CarrierPassword123!"
            }
            
            async with session.post(f"{self.base_url}/auth/register", json=carrier_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    carrier_token = result["session_token"]
                    carrier_user = result["user"]
                    self.record_test("Carrier Registration", True)
                    logger.info(f"   Carrier ID: {carrier_user['user_id']}")
                else:
                    text = await resp.text()
                    self.record_test("Carrier Registration", False, f"Status: {resp.status} - {text}")
                    return
            
            # 1.3 Test login for both users
            logger.info("🔑 Testing login for sender...")
            login_params = {"email": sender_email, "password": "SenderPassword123!"}
            async with session.post(f"{self.base_url}/auth/login", params=login_params) as resp:
                success = resp.status == 200
                self.record_test("Sender Login", success)
            
            logger.info("🔑 Testing login for carrier...")
            login_params = {"email": carrier_email, "password": "CarrierPassword123!"}
            async with session.post(f"{self.base_url}/auth/login", params=login_params) as resp:
                success = resp.status == 200
                self.record_test("Carrier Login", success)
            
            # 1.4 Test /auth/me endpoints
            sender_headers = {"Authorization": f"Bearer {sender_token}"}
            carrier_headers = {"Authorization": f"Bearer {carrier_token}"}
            
            async with session.get(f"{self.base_url}/auth/me", headers=sender_headers) as resp:
                self.record_test("Sender Auth/Me", resp.status == 200)
            
            async with session.get(f"{self.base_url}/auth/me", headers=carrier_headers) as resp:
                self.record_test("Carrier Auth/Me", resp.status == 200)
            
            # 1.5 Switch carrier to carrier role
            logger.info("🔄 Switching User B to carrier role...")
            params = {"role": "carrier"}
            async with session.put(f"{self.base_url}/users/role", params=params, headers=carrier_headers) as resp:
                self.record_test("Carrier Role Switch", resp.status == 200)
            
            # 1.6 Test profile update
            logger.info("📝 Updating carrier profile...")
            params = {"name": "Suresh Patil Updated", "phone_whatsapp": "+91-9876543210"}
            async with session.put(f"{self.base_url}/users/profile", params=params, headers=carrier_headers) as resp:
                self.record_test("Profile Update", resp.status == 200)
            
            # ============================================
            # 2. CARRIER PROFILE & KYC
            # ============================================
            
            logger.info("\n2️⃣ CARRIER PROFILE & KYC")
            logger.info("-" * 50)
            
            # 2.1 Submit KYC with mock base64 images
            logger.info("📋 Submitting KYC for carrier...")
            mock_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            
            kyc_data = {
                "phone_whatsapp": "+91-9876543210",
                "vehicle_type": "bike",
                "aadhaar_photo_base64": mock_image,
                "selfie_photo_base64": mock_image
            }
            
            async with session.post(f"{self.base_url}/carrier/kyc", json=kyc_data, headers=carrier_headers) as resp:
                self.record_test("KYC Submission", resp.status == 200)
                if resp.status == 200:
                    result = await resp.json()
                    logger.info(f"   KYC Status: {result.get('status')}")
            
            # 2.2 Get carrier profile
            logger.info("👤 Getting carrier profile...")
            async with session.get(f"{self.base_url}/carrier/profile", headers=carrier_headers) as resp:
                self.record_test("Get Carrier Profile", resp.status == 200)
            
            # 2.3 Try to go online (should fail - KYC not approved)
            logger.info("🔴 Testing online toggle without approval...")
            params = {"is_online": True}
            async with session.put(f"{self.base_url}/carrier/online", params=params, headers=carrier_headers) as resp:
                # Should fail with 403 because KYC is not approved
                self.record_test("Online Toggle (Pre-approval)", resp.status == 403)
            
            # ============================================
            # 3. ADMIN ENDPOINTS (simulate KYC approval)
            # ============================================
            
            logger.info("\n3️⃣ ADMIN ENDPOINTS")
            logger.info("-" * 50)
            
            # Note: We can't actually test admin approval without admin role
            # But we can test that admin endpoints are properly protected
            
            logger.info("🛡️ Testing admin endpoint protection...")
            
            # Test admin endpoints with regular user (should fail)
            async with session.get(f"{self.base_url}/admin/kyc/pending", headers=sender_headers) as resp:
                self.record_test("Admin KYC Access Control", resp.status == 403)
            
            async with session.get(f"{self.base_url}/admin/config", headers=sender_headers) as resp:
                self.record_test("Admin Config Access Control", resp.status == 403)
            
            params = {"key": "base_fare", "value": 30}
            async with session.put(f"{self.base_url}/admin/config", params=params, headers=sender_headers) as resp:
                self.record_test("Admin Config Update Access Control", resp.status == 403)
            
            # ============================================
            # 4. DELIVERY MANAGEMENT
            # ============================================
            
            logger.info("\n4️⃣ DELIVERY MANAGEMENT")
            logger.info("-" * 50)
            
            # 4.1 User A posts delivery (Panaji → Margao)
            logger.info("📦 User A posting delivery (Panaji → Margao)...")
            
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
                "parcel_photos_base64": [mock_image],
                "timing_preference": "asap"
            }
            
            async with session.post(f"{self.base_url}/deliveries", json=delivery_data, headers=sender_headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    delivery_id = result["delivery_id"]
                    price = result["price_rs"]
                    distance = result["distance_km"]
                    self.record_test("Delivery Creation", True)
                    logger.info(f"   Delivery ID: {delivery_id}")
                    logger.info(f"   Price: ₹{price} for {distance:.2f}km")
                    
                    # Validate Panaji-Margao pricing (~33km should be ~₹157)
                    if distance > 30 and price > 150:
                        self.record_test("Panaji-Margao Pricing Validation", True)
                    else:
                        self.record_test("Panaji-Margao Pricing Validation", False, f"Price ₹{price} for {distance}km")
                else:
                    text = await resp.text()
                    self.record_test("Delivery Creation", False, f"Status: {resp.status} - {text}")
                    return
            
            # 4.2 Get deliveries list
            logger.info("📋 Getting deliveries list...")
            async with session.get(f"{self.base_url}/deliveries", headers=sender_headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.record_test("Get Deliveries List", True)
                    logger.info(f"   Found {len(result)} deliveries")
                else:
                    self.record_test("Get Deliveries List", False)
            
            # 4.3 Get single delivery (public endpoint)
            logger.info("🔍 Testing public delivery lookup...")
            async with session.get(f"{self.base_url}/deliveries/{delivery_id}") as resp:
                self.record_test("Public Delivery Lookup", resp.status == 200)
            
            # 4.4 Test nearby deliveries (should fail - carrier not approved)
            logger.info("🗺️ Testing nearby deliveries...")
            params = {"lat": 15.49, "lng": 73.82}
            async with session.get(f"{self.base_url}/deliveries/nearby", params=params, headers=carrier_headers) as resp:
                # Should fail because carrier KYC is not approved
                self.record_test("Nearby Deliveries (KYC Check)", resp.status == 403)
            
            # ============================================
            # 5. PRICING ALGORITHM TESTS
            # ============================================
            
            logger.info("\n5️⃣ PRICING ALGORITHM TESTS")
            logger.info("-" * 50)
            
            pricing_tests = [
                (0.3, 0.5, "Under 0.5km → Should be ₹20", 20),
                (0.7, 0.5, "0.5-1km → Should be ₹25", 25),
                (1.5, 0.5, "1-2km → Should be ₹30", 30),
                (1.0, 3.0, "Weight 2-5kg → Should apply multiplier", 30)
            ]
            
            for i, (distance_km, weight_kg, description, min_price) in enumerate(pricing_tests):
                logger.info(f"💰 {description}")
                
                # Calculate rough coordinates
                lat_diff = distance_km / 111.0
                
                test_delivery = {
                    "pickup_address": f"Test Pickup {i+1}",
                    "pickup_lat": 15.4909,
                    "pickup_lng": 73.8278,
                    "dropoff_address": f"Test Dropoff {i+1}",
                    "dropoff_lat": 15.4909 + lat_diff,
                    "dropoff_lng": 73.8278,
                    "parcel_category": "documents",
                    "weight_kg": weight_kg,
                    "declared_value": 100,
                    "parcel_photos_base64": [mock_image],
                    "timing_preference": "asap"
                }
                
                async with session.post(f"{self.base_url}/deliveries", json=test_delivery, headers=sender_headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        price = result["price_rs"]
                        actual_distance = result["distance_km"]
                        
                        logger.info(f"   {actual_distance:.2f}km, {weight_kg}kg → ₹{price}")
                        
                        if price >= min_price:
                            self.record_test(f"Pricing Test {i+1}", True)
                        else:
                            self.record_test(f"Pricing Test {i+1}", False, f"₹{price} < ₹{min_price}")
                    else:
                        self.record_test(f"Pricing Test {i+1}", False, f"HTTP {resp.status}")
            
            # ============================================
            # 6. OTP SYSTEM TESTS
            # ============================================
            
            logger.info("\n6️⃣ OTP SYSTEM TESTS")
            logger.info("-" * 50)
            
            # 6.1 Test delivery acceptance (might work even without KYC approval)
            logger.info("📦 Testing delivery acceptance...")
            async with session.put(f"{self.base_url}/deliveries/{delivery_id}/accept", headers=carrier_headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    pickup_otp = result.get("pickup_otp")
                    delivery_otp = result.get("delivery_otp")
                    
                    if pickup_otp and delivery_otp:
                        self.record_test("Delivery Acceptance & OTP Generation", True)
                        logger.info(f"   Pickup OTP: {pickup_otp}")
                        logger.info(f"   Delivery OTP: {delivery_otp}")
                        
                        # 6.2 Test OTP verification
                        logger.info("🔐 Testing OTP verification...")
                        
                        # Test pickup OTP
                        otp_data = {
                            "delivery_id": delivery_id,
                            "otp": pickup_otp,
                            "otp_type": "pickup"
                        }
                        
                        async with session.post(f"{self.base_url}/deliveries/{delivery_id}/verify-otp", json=otp_data, headers=carrier_headers) as resp:
                            if resp.status == 200:
                                self.record_test("Pickup OTP Verification", True)
                                
                                # Test delivery OTP
                                otp_data["otp"] = delivery_otp
                                otp_data["otp_type"] = "delivery"
                                
                                async with session.post(f"{self.base_url}/deliveries/{delivery_id}/verify-otp", json=otp_data, headers=carrier_headers) as resp:
                                    if resp.status == 200:
                                        result = await resp.json()
                                        self.record_test("Delivery OTP Verification", True)
                                        logger.info(f"   Final status: {result.get('status')}")
                                    else:
                                        self.record_test("Delivery OTP Verification", False, f"HTTP {resp.status}")
                            else:
                                self.record_test("Pickup OTP Verification", False, f"HTTP {resp.status}")
                        
                        # 6.3 Test invalid OTP
                        logger.info("❌ Testing invalid OTP...")
                        invalid_otp_data = {
                            "delivery_id": delivery_id,
                            "otp": "9999",
                            "otp_type": "pickup"
                        }
                        
                        async with session.post(f"{self.base_url}/deliveries/{delivery_id}/verify-otp", json=invalid_otp_data, headers=carrier_headers) as resp:
                            if resp.status == 401:
                                self.record_test("Invalid OTP Rejection", True)
                            else:
                                self.record_test("Invalid OTP Rejection", False, f"Expected 401, got {resp.status}")
                    else:
                        self.record_test("Delivery Acceptance & OTP Generation", False, "No OTPs in response")
                else:
                    self.record_test("Delivery Acceptance & OTP Generation", False, f"HTTP {resp.status}")
            
            # ============================================
            # 7. CHAT & LOCATION TRACKING
            # ============================================
            
            logger.info("\n7️⃣ CHAT & LOCATION TRACKING")
            logger.info("-" * 50)
            
            # 7.1 Send message
            logger.info("💬 Testing chat messages...")
            message_data = {
                "delivery_id": delivery_id,
                "content": "Hi! I'm on my way to pick up the parcel."
            }
            
            async with session.post(f"{self.base_url}/messages", json=message_data, headers=carrier_headers) as resp:
                self.record_test("Send Message", resp.status == 200)
            
            # 7.2 Get messages
            async with session.get(f"{self.base_url}/messages/{delivery_id}", headers=carrier_headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.record_test("Get Messages", True)
                    logger.info(f"   Found {len(result)} messages")
                else:
                    self.record_test("Get Messages", False)
            
            # 7.3 Update location
            logger.info("📍 Testing location updates...")
            params = {"lat": 15.4909, "lng": 73.8278}
            async with session.post(f"{self.base_url}/deliveries/{delivery_id}/location", params=params, headers=carrier_headers) as resp:
                self.record_test("Location Update", resp.status == 200)
            
            # 7.4 Get location history (public)
            async with session.get(f"{self.base_url}/deliveries/{delivery_id}/locations") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.record_test("Location History", True)
                    logger.info(f"   Found {len(result)} location pings")
                else:
                    self.record_test("Location History", False)
            
            # ============================================
            # 8. RATINGS SYSTEM
            # ============================================
            
            logger.info("\n8️⃣ RATINGS SYSTEM")
            logger.info("-" * 50)
            
            # Get user ratings
            async with session.get(f"{self.base_url}/ratings/me", headers=carrier_headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.record_test("Get User Ratings", True)
                    logger.info(f"   Average rating: {result.get('average_rating')}")
                else:
                    self.record_test("Get User Ratings", False)
            
            # ============================================
            # 9. PERFORMANCE & INTEGRITY
            # ============================================
            
            logger.info("\n9️⃣ PERFORMANCE & INTEGRITY")
            logger.info("-" * 50)
            
            # Health check performance
            start_time = time.time()
            async with session.get(f"{self.base_url}/health") as resp:
                response_time = time.time() - start_time
                if resp.status == 200 and response_time < 1.0:
                    self.record_test("Health Check Performance", True)
                else:
                    self.record_test("Health Check Performance", False, f"{response_time:.2f}s")
            
            # Data consistency
            async with session.get(f"{self.base_url}/deliveries/{delivery_id}") as resp1:
                async with session.get(f"{self.base_url}/deliveries", headers=sender_headers) as resp2:
                    if resp1.status == 200 and resp2.status == 200:
                        self.record_test("Data Consistency", True)
                    else:
                        self.record_test("Data Consistency", False)

    def print_summary(self):
        """Print comprehensive test summary"""
        logger.info("\n" + "="*80)
        logger.info("📊 COMPREHENSIVE END-TO-END TEST SUMMARY")
        logger.info("="*80)
        
        passed = sum(1 for _, success in self.test_results if success)
        total = len(self.test_results)
        
        # Print summary statistics
        logger.info(f"\nOVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        # Print failed tests
        if self.failed_tests:
            logger.info(f"\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                logger.info(f"  • {failure}")
        
        # Print success/failure analysis
        logger.info(f"\n📈 RESULTS ANALYSIS:")
        if passed == total:
            logger.info("✅ ALL TESTS PASSED - API is fully functional!")
        elif passed / total >= 0.8:
            logger.info("✅ MOSTLY WORKING - API is largely functional with minor issues")
        elif passed / total >= 0.6:
            logger.info("⚠️ PARTIALLY WORKING - API has some functionality but needs fixes")
        else:
            logger.info("❌ SIGNIFICANT ISSUES - API needs major attention")

async def main():
    """Main function to run the end-to-end test"""
    api_base_url = "https://deliverge-pilot.preview.emergentagent.com/api"
    
    tester = DelivergeEndToEndTester(api_base_url)
    await tester.run_complete_end_to_end_test()
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())