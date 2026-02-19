#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_final_comprehensive_test():
    """Run final comprehensive test of all DELIVERGE endpoints"""
    base_url = "https://deliverge-pilot.preview.emergentagent.com/api"
    
    results = []
    failed_tests = []
    
    def record_test(name, success, details=""):
        results.append((name, success))
        if not success:
            failed_tests.append(f"{name}: {details}")
        status = "✅" if success else "❌"
        logger.info(f"{status} {name}")
    
    async with aiohttp.ClientSession() as session:
        
        logger.info("🚀 DELIVERGE API COMPREHENSIVE TEST")
        logger.info("="*60)
        
        # Create unique test users
        timestamp = int(time.time())
        sender_email = f"sender{timestamp}@example.com"
        carrier_email = f"carrier{timestamp}@example.com"
        
        # ============================================
        # 1. AUTHENTICATION & USER MANAGEMENT
        # ============================================
        
        logger.info("\n1. AUTHENTICATION & USER MANAGEMENT")
        logger.info("-" * 40)
        
        # Register sender
        sender_data = {
            "name": "Test Sender",
            "email": sender_email,
            "password": "Password123!"
        }
        
        async with session.post(f"{base_url}/auth/register", json=sender_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                sender_token = result["session_token"]
                record_test("POST /auth/register (sender)", True)
            else:
                record_test("POST /auth/register (sender)", False, f"Status: {resp.status}")
                return
        
        # Register carrier
        carrier_data = {
            "name": "Test Carrier",
            "email": carrier_email,
            "password": "Password123!"
        }
        
        async with session.post(f"{base_url}/auth/register", json=carrier_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                carrier_token = result["session_token"]
                carrier_user_id = result["user"]["user_id"]
                record_test("POST /auth/register (carrier)", True)
            else:
                record_test("POST /auth/register (carrier)", False, f"Status: {resp.status}")
                return
        
        # Test login
        login_params = {"email": sender_email, "password": "Password123!"}
        async with session.post(f"{base_url}/auth/login", params=login_params) as resp:
            record_test("POST /auth/login", resp.status == 200)
        
        # Test /auth/me
        headers = {"Authorization": f"Bearer {sender_token}"}
        async with session.get(f"{base_url}/auth/me", headers=headers) as resp:
            record_test("GET /auth/me", resp.status == 200)
        
        # Test role switch
        params = {"role": "carrier"}
        carrier_headers = {"Authorization": f"Bearer {carrier_token}"}
        async with session.put(f"{base_url}/users/role", params=params, headers=carrier_headers) as resp:
            record_test("PUT /users/role", resp.status == 200)
        
        # Test profile update
        params = {"name": "Updated Name", "phone_whatsapp": "+91-9876543210"}
        async with session.put(f"{base_url}/users/profile", params=params, headers=carrier_headers) as resp:
            record_test("PUT /users/profile", resp.status == 200)
        
        # Test logout
        async with session.post(f"{base_url}/auth/logout", headers=headers) as resp:
            record_test("POST /auth/logout", resp.status == 200)
        
        # ============================================
        # 2. CARRIER PROFILE & KYC
        # ============================================
        
        logger.info("\n2. CARRIER PROFILE & KYC")
        logger.info("-" * 40)
        
        # Submit KYC
        mock_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        kyc_data = {
            "phone_whatsapp": "+91-9876543210",
            "vehicle_type": "bike",
            "aadhaar_photo_base64": mock_image,
            "selfie_photo_base64": mock_image
        }
        
        async with session.post(f"{base_url}/carrier/kyc", json=kyc_data, headers=carrier_headers) as resp:
            record_test("POST /carrier/kyc", resp.status == 200)
        
        # Get carrier profile
        async with session.get(f"{base_url}/carrier/profile", headers=carrier_headers) as resp:
            record_test("GET /carrier/profile", resp.status == 200)
        
        # Try to go online (should fail - not approved)
        params = {"is_online": "true"}  # Use string instead of boolean
        async with session.put(f"{base_url}/carrier/online", params=params, headers=carrier_headers) as resp:
            record_test("PUT /carrier/online (pre-approval)", resp.status == 403)
        
        # ============================================
        # 3. DELIVERY MANAGEMENT
        # ============================================
        
        logger.info("\n3. DELIVERY MANAGEMENT")
        logger.info("-" * 40)
        
        # Create delivery (Panaji to Margao)
        delivery_data = {
            "pickup_address": "Panaji, Goa",
            "pickup_lat": 15.4909,
            "pickup_lng": 73.8278,
            "dropoff_address": "Margao, Goa",
            "dropoff_lat": 15.2832,
            "dropoff_lng": 73.9685,
            "parcel_category": "documents",
            "weight_kg": 0.5,
            "declared_value": 500,
            "parcel_photos_base64": [mock_image],
            "timing_preference": "asap"
        }
        
        async with session.post(f"{base_url}/deliveries", json=delivery_data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                delivery_id = result["delivery_id"]
                price = result["price_rs"]
                distance = result["distance_km"]
                record_test("POST /deliveries (Panaji→Margao)", True)
                logger.info(f"   Price: ₹{price}, Distance: {distance:.2f}km")
            else:
                record_test("POST /deliveries (Panaji→Margao)", False, f"Status: {resp.status}")
                return
        
        # Get deliveries
        async with session.get(f"{base_url}/deliveries", headers=headers) as resp:
            record_test("GET /deliveries", resp.status == 200)
        
        # Get nearby deliveries (should fail - carrier not approved)
        params = {"lat": "15.49", "lng": "73.82"}
        async with session.get(f"{base_url}/deliveries/nearby", params=params, headers=carrier_headers) as resp:
            record_test("GET /deliveries/nearby (KYC check)", resp.status == 403)
        
        # Get single delivery (public)
        async with session.get(f"{base_url}/deliveries/{delivery_id}") as resp:
            record_test("GET /deliveries/{id}", resp.status == 200)
        
        # Try to accept delivery
        async with session.put(f"{base_url}/deliveries/{delivery_id}/accept", headers=carrier_headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                pickup_otp = result.get("pickup_otp")
                delivery_otp = result.get("delivery_otp")
                record_test("PUT /deliveries/{id}/accept", True)
                logger.info(f"   OTPs generated: {pickup_otp}, {delivery_otp}")
                
                # Test OTP verification
                if pickup_otp:
                    otp_data = {
                        "delivery_id": delivery_id,
                        "otp": pickup_otp,
                        "otp_type": "pickup"
                    }
                    
                    async with session.post(f"{base_url}/deliveries/{delivery_id}/verify-otp", json=otp_data, headers=carrier_headers) as resp:
                        record_test("POST /deliveries/{id}/verify-otp (pickup)", resp.status == 200)
                    
                    # Test delivery OTP
                    otp_data["otp"] = delivery_otp
                    otp_data["otp_type"] = "delivery"
                    
                    async with session.post(f"{base_url}/deliveries/{delivery_id}/verify-otp", json=otp_data, headers=carrier_headers) as resp:
                        record_test("POST /deliveries/{id}/verify-otp (delivery)", resp.status == 200)
            else:
                record_test("PUT /deliveries/{id}/accept", False, f"Status: {resp.status}")
        
        # ============================================
        # 4. PRICING ALGORITHM TESTS
        # ============================================
        
        logger.info("\n4. PRICING ALGORITHM TESTS")
        logger.info("-" * 40)
        
        pricing_tests = [
            (0.3, 0.5, "Under 0.5km", 20),
            (0.7, 0.5, "0.5-1km", 25),
            (1.5, 0.5, "1-2km", 30),
            (33, 0.5, "33km", 150)
        ]
        
        for i, (distance_km, weight_kg, desc, min_price) in enumerate(pricing_tests):
            lat_diff = distance_km / 111.0
            
            test_delivery = {
                "pickup_address": f"Test {i}",
                "pickup_lat": 15.4909,
                "pickup_lng": 73.8278,
                "dropoff_address": f"Test Drop {i}",
                "dropoff_lat": 15.4909 + lat_diff,
                "dropoff_lng": 73.8278,
                "parcel_category": "documents",
                "weight_kg": weight_kg,
                "declared_value": 100,
                "parcel_photos_base64": [mock_image],
                "timing_preference": "asap"
            }
            
            async with session.post(f"{base_url}/deliveries", json=test_delivery, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    price = result["price_rs"]
                    actual_distance = result["distance_km"]
                    
                    success = price >= min_price
                    record_test(f"Pricing {desc}", success)
                    logger.info(f"   {actual_distance:.2f}km → ₹{price}")
                else:
                    record_test(f"Pricing {desc}", False)
        
        # ============================================
        # 5. CHAT & LOCATION
        # ============================================
        
        logger.info("\n5. CHAT & LOCATION")
        logger.info("-" * 40)
        
        # Send message
        message_data = {
            "delivery_id": delivery_id,
            "content": "Test message"
        }
        
        async with session.post(f"{base_url}/messages", json=message_data, headers=carrier_headers) as resp:
            record_test("POST /messages", resp.status == 200)
        
        # Get messages
        async with session.get(f"{base_url}/messages/{delivery_id}", headers=carrier_headers) as resp:
            record_test("GET /messages/{delivery_id}", resp.status == 200)
        
        # Update location
        params = {"lat": "15.4909", "lng": "73.8278"}
        async with session.post(f"{base_url}/deliveries/{delivery_id}/location", params=params, headers=carrier_headers) as resp:
            record_test("POST /deliveries/{id}/location", resp.status == 200)
        
        # Get location history
        async with session.get(f"{base_url}/deliveries/{delivery_id}/locations") as resp:
            record_test("GET /deliveries/{id}/locations", resp.status == 200)
        
        # ============================================
        # 6. ADMIN ENDPOINTS
        # ============================================
        
        logger.info("\n6. ADMIN ENDPOINTS")
        logger.info("-" * 40)
        
        # Test admin endpoints (should be protected)
        async with session.get(f"{base_url}/admin/kyc/pending", headers=headers) as resp:
            record_test("GET /admin/kyc/pending (protection)", resp.status == 403)
        
        async with session.put(f"{base_url}/admin/kyc/{carrier_user_id}/approve", headers=headers) as resp:
            record_test("PUT /admin/kyc/{id}/approve (protection)", resp.status == 403)
        
        async with session.get(f"{base_url}/admin/config", headers=headers) as resp:
            record_test("GET /admin/config (protection)", resp.status == 403)
        
        params = {"key": "base_fare", "value": "30"}
        async with session.put(f"{base_url}/admin/config", params=params, headers=headers) as resp:
            record_test("PUT /admin/config (protection)", resp.status == 403)
        
        # ============================================
        # 7. RATINGS & MISC
        # ============================================
        
        logger.info("\n7. RATINGS & PERFORMANCE")
        logger.info("-" * 40)
        
        # Get ratings
        async with session.get(f"{base_url}/ratings/me", headers=carrier_headers) as resp:
            record_test("GET /ratings/me", resp.status == 200)
        
        # Health check
        async with session.get(f"{base_url}/health") as resp:
            record_test("GET /health", resp.status == 200)
        
        # Root endpoint
        async with session.get(f"{base_url}/") as resp:
            record_test("GET / (root)", resp.status == 200)
    
    # ============================================
    # PRINT SUMMARY
    # ============================================
    
    logger.info("\n" + "="*60)
    logger.info("📊 FINAL COMPREHENSIVE TEST RESULTS")
    logger.info("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    logger.info(f"\nOVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    # Group by categories
    categories = {
        "Authentication": [r for r in results if "auth" in r[0].lower() or "login" in r[0].lower()],
        "User Management": [r for r in results if "users" in r[0].lower() or "profile" in r[0].lower()],
        "Carrier & KYC": [r for r in results if "carrier" in r[0].lower() or "kyc" in r[0].lower()],
        "Delivery Management": [r for r in results if "deliveries" in r[0].lower() and "pricing" not in r[0].lower()],
        "Pricing Algorithm": [r for r in results if "pricing" in r[0].lower()],
        "Chat & Location": [r for r in results if "messages" in r[0].lower() or "location" in r[0].lower()],
        "Admin Endpoints": [r for r in results if "admin" in r[0].lower()],
        "System": [r for r in results if "health" in r[0].lower() or "root" in r[0].lower() or "ratings" in r[0].lower()]
    }
    
    logger.info(f"\n📋 BY CATEGORY:")
    for category, tests in categories.items():
        if tests:
            cat_passed = sum(1 for _, success in tests if success)
            cat_total = len(tests)
            logger.info(f"  {category}: {cat_passed}/{cat_total} ({cat_passed/cat_total*100:.1f}%)")
    
    if failed_tests:
        logger.info(f"\n❌ FAILED TESTS:")
        for failure in failed_tests:
            logger.info(f"  • {failure}")
    
    logger.info(f"\n📈 ASSESSMENT:")
    if passed == total:
        logger.info("🎉 EXCELLENT - All endpoints working perfectly!")
    elif passed / total >= 0.9:
        logger.info("✅ VERY GOOD - API is fully functional with minor issues")
    elif passed / total >= 0.8:
        logger.info("✅ GOOD - API is largely functional")
    elif passed / total >= 0.7:
        logger.info("⚠️ FAIR - API has functionality but needs some fixes")
    else:
        logger.info("❌ NEEDS WORK - API has significant issues")

if __name__ == "__main__":
    asyncio.run(run_final_comprehensive_test())