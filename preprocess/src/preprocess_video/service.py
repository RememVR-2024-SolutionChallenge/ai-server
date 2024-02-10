import asyncio
import os

async def run_preprocess():
    data_existing_folder = "example_folder"
    video_data_name = "example_video.mp4"
    output_dir = "/workspace/preprocess_data"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    command = [
        "ns-process-data",
        "video",
        "--data",
        f"/workspace/{data_existing_folder}/{video_data_name}",
        "--output-dir",
        output_dir
    ]
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        return {"success": False, "error": stderr.decode().strip()}
    
    return {"success": True, "message": "Preprocessing completed successfully", "stdout": stdout.decode().strip()}
