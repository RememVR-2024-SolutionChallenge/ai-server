## 🔎 Overview
This repository implements the `Video2VR` pipeline, transforming user-input videos into 3D models compatible with WebXR viewer. Powered by NeRFStudio and MobileNeRF technologies.

## 🛠️ Architecture
TODO: insert architecture image from drawio

## 🤖 Features
### Pipeline Overview

| Preprocessing                                  | Training                                                                                      | Postprocessing                                                                    |
|------------------------------------------------|-----------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Input videos are preprocessed using NeRFStudio | Utilizing MobileNeRF as the foundation, our model undergoes a two-stage training process. | Following training, the model is postprocessed to ensure compatibility with WebXR Viewer. |


## 🙆‍♂️	User Guide

### 🙆‍♂️ Dataset Preparation Guidelines

| Scene Type   | Preview       | Recommendations                                                                     | Test Dataset Used                                       | License                |
|--------------|------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------|------------------------|
| Forwardfaced | [![Dataset Preview](./assets/faceforwarding.gif)](https://www.matthewtancik.com/nerf) | - Capture indoor or limited outdoor spaces from the front. Record videos from multiple angles facing forward. | [nerf_llff_data](https://www.matthewtancik.com/nerf) | CC BY 4.0 |
| Unbounded    | [![Dataset Preview](./assets/unbound.gif)](https://jonbarron.info/mipnerf360/)| - Capture indoor or limited outdoor spaces from the front. Record videos from multiple angles facing forward. Aim for 2~5 minute videos with detailed content. | [Tanks and Temples](https://www.tanksandtemples.org/download/) <br> [Mip-NeRF 360](https://jonbarron.info/mipnerf360/) | CC BY 4.0 |
| Indoor       | [![Dataset Preview](./assets/indoor.gif)](https://github.com/Phog/DeepBlending) | - Capture interior spaces from various angles and heights. If possible, capture the ceiling as well. Avoid capturing entire houses in one go; opt for room-sized data. | [Deep Blending](https://github.com/Phog/DeepBlending) | Apache-2.0 license |


## 👨‍💻 Developer Guide

### 👨‍💻 Run with Docker & GCP
1. Clone this repository.
2. Set up GCP credentials.
3. Build the Docker image:
```
docker build -t MY_CONTAINER_NAME .
```

4. Run the container with **volume binding**:
```
docker run -d \
   -p 8080:8080 \
   -v $PWD:/app \
   MY_CONTAINER_NAME
```

## 🔖 References
- MobileNeRF: Exploiting the Polygon Rasterization Pipeline for Efficient Neural Field Rendering on Mobile Architectures [[Link]](https://mobile-nerf.github.io/) [Apache 2.0]
- MobileNeRF + WebXR [[Link]](https://github.com/mrxz/mobilenerf-viewer-webxr) [Apache 2.0]
- HumanNeRF: Free-viewpoint Rendering of Moving People from Monocular Video [[Link]](https://github.com/chungyiweng/humannerf) [MIT]
- AvatarSDK [[Link]](https://github.com/avatarsdk/samples-js) [BSD-3-Clause]
- Google Draco [[Link]](https://github.com/google/draco) [Apache 2.0]