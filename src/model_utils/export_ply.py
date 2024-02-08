import asyncio

async def export_ply(config_base_dir: str):
    export_command = [
        "ns-export",
        "pointcloud",
        "--load-config", f"{config_base_dir}/config.yml",
        "--output-dir", "/workspace/exports/pcd/",
        "--num-points", "1000000",
        "--remove-outliers", "True",
        "--estimate-normals", "False",
        "--use-bounding-box", "True",
        "--bounding-box-min", "-5", "-5", "-5",
        "--bounding-box-max", "5", "5", "5"
    ]
    
    process = await asyncio.create_subprocess_exec(
        *export_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Export failed: {stderr.decode().strip()}")

    print(f"Export completed successfully: {stdout.decode().strip()}")
    return "/workspace/exports/pcd/"
