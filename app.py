from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from cachetools import TTLCache
import sys
import os
import lib2
import json
import asyncio

app = Flask(__name__)
CORS(app)

# Ensure current folder is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cache
cache = TTLCache(maxsize=100, ttl=300)

def cached_endpoint(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = (request.path, tuple(request.args.items()))
            if cache_key in cache:
                return cache[cache_key]
            else:
                result = func(*args, **kwargs)
                cache[cache_key] = result
                return result
        return wrapper
    return decorator

@app.route('/account')
@cached_endpoint()
def get_account_info():
    region = request.args.get('region')
    uid = request.args.get('uid')

    if not uid:
        return jsonify({
            "error": "Invalid request",
            "message": "Empty 'uid' parameter. Please provide a valid 'uid'."
        }), 400

    if not region:
        return jsonify({
            "error": "Invalid request",
            "message": "Empty 'region' parameter. Please provide a valid 'region'."
        }), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return_data = loop.run_until_complete(
            lib2.GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow")
        )
    finally:
        loop.close()

    return jsonify(return_data)

if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")
