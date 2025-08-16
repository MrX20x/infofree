from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
import lib2
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache (5 minutes)
cache = TTLCache(maxsize=100, ttl=300)

def cached_endpoint(func):
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        cache_key = (str(request.url.path), tuple(sorted(request.query_params.items())))
        if cache_key in cache:
            return cache[cache_key]
        else:
            result = await func(*args, **kwargs)
            cache[cache_key] = result
            return result
    return wrapper


@app.get("/api/account")
@cached_endpoint
async def get_account_info(
    request: Request,
    uid: str = Query(None),
    region: str = Query(None)
):
    if not uid:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid request", "message": "Empty 'uid' parameter."}
        )
    if not region:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid request", "message": "Empty 'region' parameter."}
        )

    return_data = await lib2.GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow")
    formatted_json = json.loads(json.dumps(return_data, ensure_ascii=False))

    return JSONResponse(content=formatted_json, media_type="application/json; charset=utf-8")
