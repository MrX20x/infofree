from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from cachetools import TTLCache
import asyncio
import lib2

app = Flask(__name__)
CORS(app)

cache = TTLCache(maxsize=100, ttl=300)

def cached_endpoint(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = (request.path, tuple(request.args.items()))
            if cache_key in cache:
                return cache[cache_key]
            result = func(*args, **kwargs)
            cache[cache_key] = result
            return result
        return wrapper
    return decorator

@app.route('/account')
@cached_endpoint()
def get_account_info():
    uid = request.args.get('uid')
    region = request.args.get('region')

    if not uid:
        return jsonify({"error": "Empty 'uid' parameter"}), 400
    if not region:
        return jsonify({"error": "Empty 'region' parameter"}), 400

    try:
        data = asyncio.run(
            lib2.GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow")
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
