#!/usr/bin/env python3

import asyncio
import aiohttp
import time
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_performance():
    """Test API performance and response times"""
    base_url = "https://deliverge-pilot.preview.emergentagent.com/api"
    
    logger.info("🔍 Testing API Performance...")
    
    response_times = []
    
    async with aiohttp.ClientSession() as session:
        
        # Test health endpoint performance (5 times)
        for i in range(5):
            start_time = time.time()
            try:
                async with session.get(f"{base_url}/health") as response:
                    response_time = time.time() - start_time
                    response_times.append(response_time)
                    logger.info(f"Health check #{i+1} - {response_time:.3f}s - Status: {response.status}")
            except Exception as e:
                logger.error(f"❌ Error in performance test #{i+1}: {e}")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            logger.info(f"📊 Performance Summary:")
            logger.info(f"   Average response time: {avg_time:.3f}s")
            logger.info(f"   Min response time: {min_time:.3f}s")
            logger.info(f"   Max response time: {max_time:.3f}s")
            
            if avg_time < 1.0:
                logger.info("✅ API performance is good (< 1s average)")
            elif avg_time < 2.0:
                logger.info("⚠️  API performance is acceptable (< 2s average)")
            else:
                logger.warning("❌ API performance may be slow (> 2s average)")

if __name__ == "__main__":
    asyncio.run(test_performance())