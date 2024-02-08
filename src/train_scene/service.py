import asyncio
from .model_utils import export_ply

async def run_train_scene():
    command = [
        "ns-train",
        "nerfacto",
        "--data",
        "/workspace/preprocessed_data"
    ]
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        return {"success": False, "error": stderr.decode().strip()}

    config_base_dir = "/path/to/ns-train/result" ## TODO
    
    try:
        export_dir = await export_ply(config_base_dir)
        ## TODO: Upload result file to cloud storage
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    return {"success": True, "message": "Training and export completed successfully."}
