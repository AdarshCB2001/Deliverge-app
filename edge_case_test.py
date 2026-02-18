#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_edge_cases():
    """Test additional edge cases for the DELIVERGE API"""
    base_url = "https://deliverge-pilot.preview.emergentagent.com/api"
    
    logger.info("🔍 Testing Additional Edge Cases...")
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Invalid endpoint
        try:
            async with session.get(f"{base_url}/nonexistent") as response:
                logger.info(f"Invalid endpoint test - Status: {response.status}")
                if response.status == 404:
                    logger.info("✅ 404 handling works correctly")
                else:
                    logger.warning(f"⚠️  Unexpected status for invalid endpoint: {response.status}")
        except Exception as e:
            logger.error(f"❌ Error testing invalid endpoint: {e}")
        
        # Test 2: Test root endpoint
        try:
            async with session.get(f"{base_url}/") as response:
                data = await response.json()
                logger.info(f"Root endpoint test - Status: {response.status}")
                if response.status == 200 and "DELIVERGE API" in str(data):
                    logger.info("✅ Root endpoint works correctly")
                else:
                    logger.warning(f"⚠️  Root endpoint issue: {data}")
        except Exception as e:
            logger.error(f"❌ Error testing root endpoint: {e}")
        
        # Test 3: CORS headers
        try:
            async with session.options(f"{base_url}/health") as response:
                logger.info(f"CORS preflight test - Status: {response.status}")
                headers = dict(response.headers)
                if 'access-control-allow-origin' in headers:
                    logger.info("✅ CORS configured correctly")
                else:
                    logger.warning("⚠️  CORS headers might be missing")
        except Exception as e:
            logger.error(f"❌ Error testing CORS: {e}")
            
        # Test 4: Malformed JSON
        try:
            async with session.post(
                f"{base_url}/auth/register",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            ) as response:
                logger.info(f"Malformed JSON test - Status: {response.status}")
                if response.status == 422:
                    logger.info("✅ JSON validation works correctly")
                else:
                    logger.warning(f"⚠️  Unexpected status for malformed JSON: {response.status}")
        except Exception as e:
            logger.error(f"❌ Error testing malformed JSON: {e}")

if __name__ == "__main__":
    asyncio.run(test_edge_cases())