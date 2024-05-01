import sys
import os
import subprocess
import logging
from argparse import ArgumentParser

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def extract_images(video_path):
    video_dir, video_name = os.path.split(video_path)
    input_dir = os.path.join(video_dir, "input")
    os.makedirs(input_dir, exist_ok=True)

    ffmpeg_cmd = [
        "ffmpeg", "-i", video_path, "-qscale:v", "1", "-qmin", "1", "-vf", "fps=1",
        os.path.join(input_dir, "%04d.jpg")
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    return video_dir

def run_colmap_commands(source_path, no_gpu):
    use_gpu = 0 if no_gpu else 1
    colmap_command = "colmap"
    os.makedirs(os.path.join(source_path, "distorted/sparse"), exist_ok=True)

    # Feature extraction
    feat_extraction_cmd = f"{colmap_command} feature_extractor --database_path {source_path}/distorted/database.db --image_path {source_path}/input --ImageReader.single_camera 1 --ImageReader.camera_model OPENCV --SiftExtraction.use_gpu {use_gpu}"
    if subprocess.run(feat_extraction_cmd, shell=True).returncode != 0:
        logging.error("colmap-0: Feature extraction failed.")
        sys.exit(1)

    # Feature matching
    feat_matching_cmd = f"{colmap_command} exhaustive_matcher --database_path {source_path}/distorted/database.db --SiftMatching.use_gpu {use_gpu}"
    if subprocess.run(feat_matching_cmd, shell=True).returncode != 0:
        logging.error("colmap-1: Feature matching failed.")
        sys.exit(1)

    # Bundle adjustment
    mapper_cmd = f"{colmap_command} mapper --database_path {source_path}/distorted/database.db --image_path {source_path}/input --output_path {source_path}/distorted/sparse --Mapper.ba_global_function_tolerance=0.000001"
    if subprocess.run(mapper_cmd, shell=True).returncode != 0:
        logging.error("colmap-2: Bundle adjustment failed.")
        sys.exit(1)

    # Image undistortion
    img_undist_cmd = f"{colmap_command} image_undistorter --image_path {source_path}/input --input_path {source_path}/distorted/sparse/0 --output_path {source_path} --output_type COLMAP"
    if subprocess.run(img_undist_cmd, shell=True).returncode != 0:
        logging.error("colmap-3: Image undistortion failed.")
        sys.exit(1)

def main(video_path, no_gpu=False):
    logger = setup_logger()
    logger.info("Starting video processing.")
    source_path = extract_images(video_path)
    run_colmap_commands(source_path, no_gpu)
    logger.info("Video processing completed successfully.")

if __name__ == "__main__":
    parser = ArgumentParser(description="Process video with FFmpeg and run COLMAP pipeline.")
    parser.add_argument("video_path", type=str, help="Path to the video file")
    parser.add_argument("--no_gpu", action='store_true', help="Disable GPU acceleration")
    args = parser.parse_args()
    main(args.video_path, args.no_gpu)