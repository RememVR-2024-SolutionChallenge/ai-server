import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"

async def run_command(*args):
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return process.returncode == 0 

async def run_train_stage1():
    return await run_command('python', str(MODEL_DIR / 'train_stage1.py'))

async def run_train_stage2():
    return await run_command('python', str(MODEL_DIR / 'train_stage2.py'))

async def run_postprocess_entire():
    return await run_command('python', str(MODEL_DIR / 'postprocess_entire.py'))
