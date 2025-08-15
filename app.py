# api/account.py
import sys
import os
import json
import asyncio
from cachetools import TTLCache

# Add project root to sys.path so 'lib2' and 'proto' can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import lib2  # your library that uses proto
# proto folder should be at the same level as lib2

# Cache with TTL of 5 minutes
cache = TTLCache(maxsize=100, ttl=300)

async def fetch_account_info(uid, region):
    """Fetch account information asynchronously"""
    return await lib2.GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow")

def handler(request):
    """Vercel serverless function handler"""
    # Extract query parameters
    query = request.args
    uid = query.get("uid")
    region = query.get("region")

    # Validation
    if not uid:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid request",
                "message": "Empty 'uid' parameter. Please provide a valid 'uid'."
            }),
            "headers": {"Content-Type": "application/json; charset=utf-8"}
        }

    if not region:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid request",
                "message": "Empty 'region' parameter. Please provide a valid 'region'."
            }),
            "headers": {"Content-Type": "application/json; charset=utf-8"}
        }

    # Check cache
    cache_key = (uid, region)
    if cache_key in cache:
        return {
            "statusCode": 200,
            "body": json.dumps(cache[cache_key], ensure_ascii=False),
            "headers": {"Content-Type": "application/json; charset=utf-8"}
        }

    # Fetch data asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(fetch_account_info(uid, region))
    loop.close()

    # Store in cache
    cache[cache_key] = data

    return {
        "statusCode": 200,
        "body": json.dumps(data, ensure_ascii=False),
        "headers": {"Content-Type": "application/json; charset=utf-8"}
    }
