from fastapi import FastAPI
from .api import api_router

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint is working"}


app.include_router(api_router)
