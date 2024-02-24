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
    
    
@app.post("/api/train-scene")
async def train_scene():
    base_dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = os.path.join(os.getcwd(), 'data', base_dir_name)
    input_dir = f"{base_dir}/input"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(input_dir, exist_ok=True)

    os.environ['BASE_DIR'] = base_dir
    env = os.environ.copy()
    
    base_dir_data = {"base_dir": base_dir}
    env_data = {"env" : env}

    ##TODO: Cloud Storage로부터 받은 Video 불러오기 -> input_dir에 저장
    ##TODO: EX. /app/data/2024-02-17-06-22-39/video.mov

    async with httpx.AsyncClient() as client:
        # Preprocess 단계 호출
        preprocess_response = await client.post(PREPROCESS_URL, json=base_dir_data)
        if preprocess_response.status_code != 200:
            raise HTTPException(status_code=preprocess_response.status_code, detail="Preprocess step failed")

        # Train 단계 호출
        mobilenerf_response = await client.post(MOBILENERF_URL, json=env_data)
        if mobilenerf_response.status_code != 200:
            raise HTTPException(status_code=mobilenerf_response.status_code, detail="Mobilenerf step failed")

        # Postprocess 단계 호출
        postprocess_response = await client.post(POSTPROCESS_URL, json=env_data)
        if postprocess_response.status_code != 200:
            raise HTTPException(status_code=postprocess_response.status_code, detail="Postprocess step failed")

    return {"message": "All stages completed successfully, files are ready in " + base_dir}


@app.post("/api/preprocess")
async def preprocess(data: Dict):
    base_dir = data.get("base_dir")
    input_dir = f"{base_dir}/input"
    preprocessed_dir = f"{base_dir}/preprocessed_input"
    os.makedirs(preprocessed_dir, exist_ok=True)

    logger.info("Preprocessing started")
    command = f"ns-process-data video --data \"{input_dir}/video.mov\" --output-dir \"{preprocessed_dir}\""

    try:
        process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("Preprocessing completed successfully.")
        return {"message": "Preprocessing completed successfully."}
    except subprocess.CalledProcessError as e:
        logger.error(f"Preprocessing failed: {e.stderr}")
        return {"detail": "Preprocessing failed", "error": e.stderr}, 400
    

@app.post("/api/mobilenerf")
async def mobilenerf(data: Dict):
    env = data.get("env")
    logger.info("Mobilenerf training started")
    subprocess.run(['python', 'train.py'], env=env)
    await asyncio.sleep(3)  # 3초 대기
    logger.info("Mobilenerf training completed successfully.")
    return {"message": "Mobilenerf training completed successfully."}


@app.post("/api/postprocess")
async def postprocess(data: Dict):
    base_dir = data.get("base_dir")
    logger.info("Postprocessing started")
    await asyncio.sleep(3)  # 3초 대기
    logger.info("Postprocessing completed successfully.")
    return {"message": "Postprocessing completed successfully."}



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
    
def get_unique_folder_name():
    now = datetime.now()
    dir_name = now.strftime("%Y-%m-%d-%H-%M-%S")
    return f"/data/{dir_name}"