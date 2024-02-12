from fastapi import APIRouter, UploadFile, File
from .schemas import VideoUpload
from .service import run_ffmpeg

router = APIRouter()

@router.post("/process-video")
async def process_video(video: UploadFile = File(...)):
    result = await run_ffmpeg(video) # TODO: implement process_video
    return {"result": result}