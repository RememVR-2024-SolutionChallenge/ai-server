import asyncio
import io
import os
import subprocess
import time
import random
from datetime import datetime
from subprocess import Popen, PIPE
from typing import Dict, List, Optional
import shutil

import httpx
from PIL import Image
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn

from common.scheduler_utils import trigger_scheduler
from common.storage_utils import download_from_storage, upload_to_storage
from common.firestore_utils import *

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
GS_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api/gs"
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

@app.post("/make-idle")
async def make_idle():
    global IS_BUSY
    IS_BUSY = False
    logger.info("This is a test log message.")
    logger.error("this is error test.")
    return {"message": "Idle"}

@app.post("/process-avatar")
async def process_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    base_dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    directory_path = os.path.join(os.getcwd(), 'test', 'data', base_dir_name)
    os.makedirs(directory_path, exist_ok=True)
    video_path = os.path.join(directory_path, file.filename)

    logger.debug("pressing video....")
    print("pressing video....")

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    background_tasks.add_task(run_preprocess, video_path)

    return {"message": "Video is being processed", "filename": file.filename}


@app.post("/process-video")
async def process_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    base_dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    directory_path = os.path.join(os.getcwd(), 'test', 'data', base_dir_name)
    os.makedirs(directory_path, exist_ok=True)
    video_path = os.path.join(directory_path, file.filename)

    logger.debug("pressing video....")
    print("pressing video....")

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    background_tasks.add_task(run_preprocess, video_path)

    return {"message": "Video is being processed", "filename": file.filename}

def run_preprocess(video_path):
    subprocess.run(["python3", "/app/model/gaussian_splatting/preprocess.py", video_path], check=True)

    
@app.post("/api/train/{doc_id}", status_code=202)
async def train_model(background_tasks: BackgroundTasks, doc_id: str):
    global IS_BUSY
    if IS_BUSY:
        return JSONResponse(status_code=400, content={"message": "Server is currently busy. Please try again later."})

    IS_BUSY = True
    dbInstance = SampleVRData() if is_sample(doc_id) else VRData()
    request_data = dbInstance.get_request(doc_id = doc_id)
    if not request_data:
        IS_BUSY = False
        return JSONResponse(status_code=404, content={"message": "Request data not found"})

    #background_tasks.add_task(execute_training_pipeline, doc_id, request_data)
    background_tasks.add_task(execute_test_pipeline, doc_id, request_data, dbInstance)
    return JSONResponse(status_code=200, content={"message": "Training started successfully"})

@app.post("/api/train-example/{doc_id}", status_code=202)
async def train_model(background_tasks: BackgroundTasks, doc_id: str):
    global IS_BUSY
    if IS_BUSY:
        return JSONResponse(status_code=400, content={"message": "Server is currently busy. Please try again later."})

    IS_BUSY = True

    background_tasks.add_task(execute_scene_async_pipeline, doc_id)
    return JSONResponse(status_code=202, content={"message": "Training started successfully"})

async def execute_scene_async_pipeline(doc_id: str):
    global IS_BUSY
    logger.info("Starting scene pipeline for doc_id:", doc_id)
    base_directory = os.path.join(os.getcwd(), "test", "data", "bedroom")
    train_cmd = (
        f"ns-train splatfacto --data \"{base_directory}\" "
        f"--output-dir \"{base_directory}/{doc_id}\" "
        f"--viewer.quit-on-train-completion True --max-num-iterations 1000"
    )

    try:
        # Run the training command asynchronously
        proc = await asyncio.create_subprocess_shell(
            train_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise Exception(f"Training failed with error: {stderr.decode()}")

        # Assume some output file handling here
        output_file_path = os.path.join(base_directory, doc_id)
        result_bytes = read_file_as_bytes(output_file_path)
        # Upload results or further processing

    except Exception as e:
        logger.error(f"An error occurred in execute_scene_pipeline: {e}, doc_id: {doc_id}")
        IS_BUSY = False
        # return JSONResponse(status_code=400, content={"message": str(e)})

    finally:
        # Cleanup
        folder_path = os.path.join(os.getcwd(), "test", "bedroom", doc_id)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        IS_BUSY = False
        trigger_scheduler()

    return {"message": "Training completed successfully"}


async def execute_scene_pipeline(doc_id: str):
    global IS_BUSY
    logger.info("execute_scene_pipeline", doc_id, "IS_BUSY", IS_BUSY)
    try:
        # Step 1: Update status to processing
        # Step 3: Main AI Process
        # 원래 AI 학습 코드가 들어가는 부분
        # 작동 확인 후 수정
        base_directory = os.path.join(os.getcwd(), "test", "data", "bedroom")
        train_cmd = f"ns-train splatfacto --data \"{base_directory}\" --output-dir \"{base_directory}/{doc_id}\" --viewer.quit-on-train-completion True --max-num-iterations 1000" # 
        subprocess.run(train_cmd, check=True, shell=True)

        # Step 4: Upload Results
        output_file_path = os.path.join(base_directory, doc_id)
        result_bytes = read_file_as_bytes(output_file_path)

    except Exception as e:
        logger.info(f"An error occurred: {e}, doc_id: {doc_id}")
        IS_BUSY = False
        # return JSONResponse(status_code=400, content={"message": f"{str(e)}"})

    # Step 6: Update server status and clean up local files
    finally:
        folder_path = os.path.join(os.getcwd(), "test", "bedroom", doc_id)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path) 
        IS_BUSY = False
        trigger_scheduler()


async def execute_test_pipeline(doc_id: str, request_data: Dict, db_instance):
    global IS_BUSY
    try:
        # Step 1: Update status to processing
        db_instance.update_request_status_processing(doc_id)

        # Step 2: Download data / Save locally
        groupId = request_data.get('groupId')
        title = request_data.get('title')
        resourceType = request_data.get('type')
        logger.info(groupId, title, resourceType)
        if resourceType == "avatar" :
            faceImagePath = request_data.get('faceImagePath')
            bodyImagePath = request_data.get('bodyImagePath')
            gender = request_data.get('gender')

            faceImageBytes = await asyncio.get_event_loop().run_in_executor(None, download_from_storage, faceImagePath)
            faceFilePath = save_bytes_to_file(faceImageBytes, "face.jpg", os.path.join(os.getcwd(), doc_id))
            bodyImageBytes = await asyncio.get_event_loop().run_in_executor(None, download_from_storage, bodyImagePath)
            bodyFilePath = save_bytes_to_file(bodyImageBytes, "body.jpg", os.path.join(os.getcwd(), doc_id))

        if resourceType == "scene" :
            sceneVideoPath = request_data.get('sceneVideoPath')
            sceneVideoBytes = await asyncio.get_event_loop().run_in_executor(None, download_from_storage, sceneVideoPath)
            sceneFilePath = save_bytes_to_file(sceneVideoBytes, "video.mp4", os.path.join(os.getcwd(), doc_id))

        # Step 3: Main AI Process
        # 작동 확인 후 모델 파이프라인으로 수정
        if title == "서영":
            sampleFilePath = "/app/test/example/seoyoung.fbx"
        elif title == "서연":
            sampleFilePath = "/app/test/example/seoyeon.fbx"
        elif title == "진우":
            sampleFilePath = "/app/test/example/jinwoo.fbx"
        elif title == "귀정" :
            sampleFilePath = "/app/test/example/guijung.fbx"

        output_file_path = os.path.join(os.getcwd(), doc_id, "output", "avatar.fbx")
        if not os.path.exists(output_file_path):
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        shutil.copyfile(sampleFilePath, output_file_path)
        result_file_path = f"3dgs-response/{doc_id}/avatar.fbx"

        logger.info("Starting scene pipeline for doc_id:", doc_id)
        base_directory = os.path.join(os.getcwd(), "test", "data", "bedroom")
        train_cmd = (
            f"ns-train splatfacto --data \"{base_directory}\" "
            f"--output-dir \"{base_directory}/{doc_id}\" "
            f"--viewer.quit-on-train-completion True --max-num-iterations 1000"
        )

        try:
            # Run the training command asynchronously
            proc = await asyncio.create_subprocess_shell(
                train_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            # if proc.returncode != 0:
            #     raise Exception(f"Training failed with error: {stderr.decode()}")
        # except Exception as e:
        except:
            logger.info(f"An error occurred: {e}, doc_id: {doc_id}")
            IS_BUSY = False
            # return JSONResponse(status_code=400, content={"message": f"{str(e)}"})

        # Step 4: Upload Results
        result_bytes = read_file_as_bytes(output_file_path)
        await asyncio.get_event_loop().run_in_executor(None, upload_to_storage, result_file_path, result_bytes, 'application/octet-stream')

        # Step 5: Update DB
        if is_sample(doc_id):
            db_instance.insert_vr_resource(doc_id, title, resourceType, result_file_path)
        else:
            db_instance.insert_vr_resource(doc_id, title, resourceType, groupId, result_file_path)
        logger.info("update request complete start")
        await asyncio.get_event_loop().run_in_executor(None, db_instance.update_request_status_completed, doc_id)
        # db_instance.update_request_status_completed(doc_id)
        logger.info("update request complete end")

    except Exception as e:
        logger.info(f"An error occurred: {e}, doc_id: {doc_id}")
        db_instance.update_request_status_failed(doc_id)
        IS_BUSY = False
        # return JSONResponse(status_code=400, detail=str(e))

    # Step 6: Update server status and clean up local files
    finally:
        logger.info(f"finally start")
        folder_path = os.path.join(os.getcwd(), doc_id)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path) 
        logger.info(f"finally make busy")
        IS_BUSY = False
        logger.info(f"start trigger_scheduler")
        try: 
            #await asyncio.get_event_loop().run_in_executor(None, trigger_scheduler)
            trigger_scheduler() # 비동기 로직
            logger.info(f"trigger_scheduler success")
        except Exception as e:
            logger.info("trigger_scheduler failed ")
            logger.info(f"An error occurred: {e}")
            


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

    if resourceType == "avatar":
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
                vrData.insert_vr_resource(doc_id, title, resourceType, groupId, output_file_path)
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

    elif resourceType == "scene":
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
    

@app.post("/api/gs")
async def mobilenerf(data: Dict):
    env = data.get("env")
    try:
        logger.info("Mobilenerf training started")
        result1 = subprocess.run(['python', './model/train_stage1.py'], env=env, check=True)
        result2 = subprocess.run(['python', './model/train_stage2.py'], env=env, check=True)
        logger.info("Mobilenerf training completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during Mobilenerf training: {e}")
        raise HTTPException(status_code=400, detail="Error occurred during Mobilenerf training.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=400, detail="Unexpected error occurred during Mobilenerf training.")
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

def save_bytes_to_file(data: bytes, file_name: str, save_path: str):
    path = os.path.join(save_path, file_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as file:
        file.write(data)
    return path

def read_file_as_bytes(filepath: str) -> bytes:
    with open(filepath, 'rb') as file:
        return file.read()


def get_content_type(file_name: str):
    _, ext = os.path.splitext(file_name)
    return {
        '.png': 'image/png',
        '.json': 'application/json',
        '.glb': 'model/gltf-binary',
        '.fbx': 'application/octet-stream',
        '.ply': 'model/ply',
    }.get(ext, 'application/octet-stream')