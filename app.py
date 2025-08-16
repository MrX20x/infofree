from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
import lib2
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = TTLCache(maxsize=100, ttl=300)

def cached_endpoint(func):
    async def wrapper(request: Request, uid: str = Query(...), region: str = Query(...)):
        cache_key = (str(request.url.path), tuple(sorted(request.query_params.items())))
        if cache_key in cache:
            return cache[cache_key]
        result = await func(request=request, uid=uid, region=region)
        cache[cache_key] = result
        return result
    return wrapper

@app.get("/api/account")
@cached_endpoint
async def get_account_info(request: Request, uid: str = Query(...), region: str = Query(...)):
    try:
        data = await lib2.GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow")
        return JSONResponse(content=json.loads(json.dumps(data, ensure_ascii=False)))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal server error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True)
