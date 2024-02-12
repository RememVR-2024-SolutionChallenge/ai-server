import subprocess

def run_train_scene():
    try:
        subprocess.run(["python", "scripts/scene_model/train.py", "-s", "temp"], check=True)
        return {"status": "success"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}