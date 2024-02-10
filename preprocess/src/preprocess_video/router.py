from fastapi import APIRouter
from .service import run_preprocess

router = APIRouter()

@router.post("/preprocess")
async def preprocess():
    result = await run_preprocess()
    return result