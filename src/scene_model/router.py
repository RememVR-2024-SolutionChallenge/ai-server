from fastapi import APIRouter
from .service import run_train_scene

router = APIRouter()

@router.post("/train-scene")
async def train_scene():
    result = run_train_scene()
    return result