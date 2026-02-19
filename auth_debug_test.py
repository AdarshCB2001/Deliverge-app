#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_auth_flow():
    """Test the authentication flow step by step"""
    base_url = "https://deliverge-pilot.preview.emergentagent.com/api"
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Test health check
        logger.info("1. Testing health check...")
        async with session.get(f"{base_url}/health") as resp:
            logger.info(f"Health check: {resp.status} - {await resp.text()}")
        
        # 2. Try to register a new user (might fail if exists)
        logger.info("2. Testing user registration...")
        user_data = {
            "name": "Test User Auth Debug",
            "email": f"test.auth.debug.{asyncio.current_task().get_name()}@example.com",
            "password": "TestPassword123!"
        }
        
        async with session.post(f"{base_url}/auth/register", json=user_data) as resp:
            register_result = await resp.json()
            logger.info(f"Registration: {resp.status} - {register_result}")
            
            if resp.status == 200:
                session_token = register_result.get("session_token")
                logger.info(f"Got session token: {session_token[:20]}..." if session_token else "No token")
            else:
                session_token = None
        
        # 3. Login with the user (should work regardless)
        logger.info("3. Testing user login...")
        login_params = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        async with session.post(f"{base_url}/auth/login", params=login_params) as resp:
            if resp.status == 200:
                login_result = await resp.json()
                session_token = login_result.get("session_token")
                user = login_result.get("user")
                logger.info(f"Login successful: {resp.status}")
                logger.info(f"Session token: {session_token[:20]}..." if session_token else "No token")
                logger.info(f"User: {user}")
            else:
                login_text = await resp.text()
                logger.error(f"Login failed: {resp.status} - {login_text}")
                return
        
        # 4. Test authenticated endpoint with Authorization header
        logger.info("4. Testing authenticated endpoint with Authorization header...")
        headers = {"Authorization": f"Bearer {session_token}"}
        
        async with session.get(f"{base_url}/auth/me", headers=headers) as resp:
            result = await resp.text()
            logger.info(f"Get current user (header): {resp.status} - {result}")
        
        # 5. Test authenticated endpoint with cookie (set manually)
        logger.info("5. Testing authenticated endpoint with cookie...")
        session.cookie_jar.update_cookies({"session_token": session_token})
        
        async with session.get(f"{base_url}/auth/me") as resp:
            result = await resp.text()
            logger.info(f"Get current user (cookie): {resp.status} - {result}")
        
        # 6. Test role switch
        logger.info("6. Testing role switch...")
        params = {"role": "carrier"}
        async with session.put(f"{base_url}/users/role", params=params, headers=headers) as resp:
            result = await resp.text()
            logger.info(f"Role switch: {resp.status} - {result}")
        
        # 7. Test delivery creation
        logger.info("7. Testing delivery creation...")
        delivery_data = {
            "pickup_address": "Test Pickup",
            "pickup_lat": 15.4909,
            "pickup_lng": 73.8278,
            "dropoff_address": "Test Dropoff", 
            "dropoff_lat": 15.2832,
            "dropoff_lng": 73.9685,
            "parcel_category": "documents",
            "weight_kg": 0.5,
            "declared_value": 100,
            "parcel_photos_base64": ["data:image/png;base64,test"],
            "timing_preference": "asap"
        }
        
        async with session.post(f"{base_url}/deliveries", json=delivery_data, headers=headers) as resp:
            result = await resp.text()
            logger.info(f"Create delivery: {resp.status} - {result}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())