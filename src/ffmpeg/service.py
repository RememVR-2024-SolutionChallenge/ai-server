import os
import shutil
import subprocess
from fastapi import UploadFile
#from .utils import prepare_data

async def run_ffmpeg(video_file: UploadFile):
    #dataname, fps = prepare_data(video_file)
    dataname = "input"
    fps = 1
    file_directory = os.path.join(".", "temp")
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)

    if not os.path.exists(os.path.join(file_directory, dataname)):
        os.makedirs(os.path.join(file_directory, dataname))
    
    file_location = os.path.join(file_directory, video_file.filename)
    with open(file_location, "wb") as file:
        shutil.copyfileobj(video_file.file, file)

    output_pattern = os.path.join(file_directory, dataname, "%04d.jpg")
    command = [
        "ffmpeg", "-i", file_location, 
        "-qscale:v", "1", "-qmin", "2", "-vf", f"fps={fps}", output_pattern ] ## TODO
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return {"stdout" : stdout, "stderr" : stderr}