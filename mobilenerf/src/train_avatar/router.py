from fastapi import APIRouter
from .service import run_train_stage1, run_train_stage2, run_postprocess_entire

router = APIRouter()

@router.get("/train-stage1")
async def train_stage1():
    if await run_train_stage1():
        return {"message": "Stage 1 training completed successfully."}
    else:
        return {"error": "Stage 1 training failed."}

@router.get("/train-stage2")
async def train_stage2():
    if await run_train_stage2():
        return {"message": "Stage 2 training completed successfully."}
    else:
        return {"error": "Stage 2 training failed."}

@router.get("/postprocess-entire")
async def postprocess_entire():
    if await run_postprocess_entire():
        return {"message": "Postprocessing completed successfully."}
    else:
        return {"error": "Postprocessing failed."}
