import asyncio
import io
import os
import subprocess
import time
from datetime import datetime
from subprocess import Popen, PIPE
from typing import Dict, List, Optional

import httpx
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from config import SERVER_IP, SERVER_PORT
from logger import logger
from pydantic import BaseModel


app = FastAPI(
    title="AI-API-SERVER",
    description="2024 GDSC Solution Challenge: RememVR AI-API-SERVER)",
    contact={
        "name": "Seoyeon Byun",
        "email": "byunhwan8832@korea.ac.kr",
    },
)


########## Management ##########
IS_BUSY = False

PREPROCESS_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api/preprocess"
MOBILENERF_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api/mobilenerf"
POSTPROCESS_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api/postprocess"

########## @@ APIHandler ##########

@app.get("/api/status")
async def checkStatus():
    global IS_BUSY
    if IS_BUSY:
        return JSONResponse(
            status_code=200, 
            content={"status": "BUSY"}
        )
    else:
        return JSONResponse(
            status_code=200, 
            content={"status": "IDLE"}
        )
    
@app.post("/train-scene")
async def train_scene():
    scripts = ["train_stage1.py", "train_stage2.py", "postprocess.py"]
    for script in scripts:
        error_message = run_script(script)
        if error_message:
            return {"success": False, "message": f"Failed at {script}: {error_message}"}
    
    output_folder = "/data/output"
    bucket_name = "your-bucket-name"
    upload_success = upload_files_to_gcs(bucket_name, output_folder)
    if upload_success:
        return {"success": True, "message": "All stages completed successfully, files uploaded to GCS."}
    else:
        return {"success": False, "message": "Failed to upload files to GCS."}


########## Training Utilities ##########
    
def run_script(script_name: str) -> Optional[str]:
    try:
        process = Popen(["python", script_name], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return stderr.decode("utf-8") 
        return None  
    except Exception as e:
        return str(e)