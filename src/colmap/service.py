import subprocess

def run_colmap():
    try:
        subprocess.run(["python", "scripts/convert.py", "-s", "temp"], check=True)
        return {"status": "success"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}
