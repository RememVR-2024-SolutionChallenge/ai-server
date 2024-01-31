from fastapi import APIRouter
from .service import run_colmap

router = APIRouter()

@router.post("/process-colmap")
async def process_colmap():
    result = run_colmap()
    return result
