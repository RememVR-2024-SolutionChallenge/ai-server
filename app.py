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
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

from common.scheduler_utils import trigger_scheduler
from common.storage_utils import download_from_storage, upload_to_storage
from common.firestore_utils import (
    get_request, 
    update_request_status_completed, 
    update_request_status_failed, 
    update_request_status_processing,
    insert_vr_resource
)

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

@app.get("/")
async def health_check():
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
    
@app.post("/api/train/{doc_id}", status_code=202)
async def train_model(background_tasks: BackgroundTasks, doc_id: str):
    global IS_BUSY
    if IS_BUSY:
        raise HTTPException(status_code=400, detail="Server is currently busy. Please try again later.")
    IS_BUSY = True

    request_data = get_request(doc_id)
    if not request_data:
        IS_BUSY = False
        raise HTTPException(status_code=404, detail="Request data not found")

    background_tasks.add_task(execute_training_pipeline, doc_id, request_data)


async def execute_training_pipeline(doc_id: str, request_data: Dict):
    global IS_BUSY
    IS_BUSY = True

    groupId = request_data.get('groupId')
    title = request_data.get('title')
    videoPath = request_data.get('videoPath')
    resourceType = request_data.get('type')

    update_request_status_processing(doc_id)

    base_dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = os.path.join(os.getcwd(), 'data', base_dir_name)
    input_dir = f"{base_dir}/input"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(input_dir, exist_ok=True)

    os.environ['BASE_DIR'] = base_dir
    env = os.environ.copy()
    
    base_dir_data = {"base_dir": base_dir}
    env_data = {"env" : env}

    try:
        video_file_bytes = download_from_storage(videoPath)
        saved_file_path = save_bytes_to_file(video_file_bytes, "video.mov", input_dir)
    except FileNotFoundError:
        logger.error("The specified video file was not found in Cloud Storage.")
        update_request_status_failed(doc_id)
        raise HTTPException(status_code=404, detail="Video file not found.")
        
    except PermissionError:
        logger.error("Permission denied while accessing the video file.")
        update_request_status_failed(doc_id)
        raise HTTPException(status_code=403, detail="Permission denied.")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        update_request_status_failed(doc_id)
        raise HTTPException(status_code=400, detail="Failed to process the video file due to an unexpected error.")


    try:
        async with httpx.AsyncClient() as client:
            preprocess_response = await client.post(PREPROCESS_URL, json=base_dir_data)
            if preprocess_response.status_code != 200:
                raise HTTPException(status_code=preprocess_response.status_code, detail="Preprocess step failed")

            mobilenerf_response = await client.post(MOBILENERF_URL, json=env_data)
            if mobilenerf_response.status_code != 200:
                raise HTTPException(status_code=mobilenerf_response.status_code, detail="Mobilenerf step failed")

            postprocess_response = await client.post(POSTPROCESS_URL, json=env_data)
            if postprocess_response.status_code != 200:
                raise HTTPException(status_code=postprocess_response.status_code, detail="Postprocess step failed")
       
        output_file_path = f"{base_dir}/output/"
        try: 
            insert_vr_resource(doc_id, title, resourceType, groupId, output_file_path)
        except Exception as e:
            logger.error(f"Error inserting VR resource: {str(e)}")
            update_request_status_failed(doc_id)
            raise HTTPException(status_code=500, detail="Failed to insert VR resource into Firestore.")

        try:
            for root, dirs, files in os.walk(output_file_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as file_data:
                        data = file_data.read()
                    content_type = get_content_type(file)
                    storage_file_path = os.path.join("test", file) 
                    upload_to_storage(storage_file_path, data, content_type)
                    
            update_request_status_completed(doc_id)
        except Exception as e:
            logger.error(f"Error uploading files: {str(e)}")
            update_request_status_failed(doc_id)
            raise HTTPException(status_code=500, detail="Failed to upload files to Cloud Storage.")


    except HTTPException as http_exc:
        logger.error(f"Error during pipeline execution: {http_exc.detail}")
        update_request_status_failed(doc_id)
        # raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)

    finally:
        IS_BUSY = False
        trigger_scheduler()

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
    try:
        logger.info("Mobilenerf training started")
        result1 = subprocess.run(['python', './model/train_stage1.py'], env=env, check=True)
        result2 = subprocess.run(['python', './model/train_stage2.py'], env=env, check=True)
        logger.info("Mobilenerf training completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during Mobilenerf training: {e}")
        raise HTTPException(status_code=500, detail="Error occurred during Mobilenerf training.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred during Mobilenerf training.")
    return {"message": "Mobilenerf training completed successfully."}

@app.post("/api/postprocess")
async def postprocess(data: Dict):
    base_dir = data.get("base_dir")
    try:
        logger.info("Postprocessing started")
        result = subprocess.run(['python', './model/postprocess_entire.py'], env=env, check=True)
        logger.info("Postprocessing completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during postprocessing: {e}")
        raise HTTPException(status_code=500, detail="Error occurred during postprocessing.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred during postprocessing.")
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

def save_bytes_to_file(file_bytes: bytes, file_name: str, save_path: str):
    save_file_path = os.path.join(save_path, file_name)
    os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
    with open(save_file_path, 'wb') as file_to_save:
        file_to_save.write(file_bytes)
    return save_file_path

def get_content_type(file_name: str):
    _, ext = os.path.splitext(file_name)
    return {
        '.png': 'image/png',
        '.json': 'application/json',
        '.glb': 'model/gltf-binary',
        '.fbx': 'application/octet-stream'
    }.get(ext, 'application/octet-stream')