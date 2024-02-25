## 🔎 Overview
This repository implements the `Video2VR` pipeline, transforming user-input videos into 3D models compatible with WebXR viewer. Powered by NeRFStudio and MobileNeRF technologies.

## 🛠️ Architecture

## 🤖 Features

## 🙍‍♂️	User Guide

### 🙍‍♂️ Dataset Preparation Guidelines

| Scene Type   | Dataset Preview       | Recommendations                                                                     | Test Dataset Used                                       | License                |
|--------------|------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------|------------------------|
| Forwardfaced | [![Dataset Preview](INSERT_IMAGE_URL)](https://www.matthewtancik.com/nerf) | - Capture indoor or limited outdoor spaces from the front. Record videos from multiple angles facing forward. | [nerf_llff_data](https://www.matthewtancik.com/nerf) | CC BY 4.0 |
| Unbounded    | [![Dataset Preview](INSERT_IMAGE_URL)](https://www.tanksandtemples.org/download/) <br> [![Dataset Preview](INSERT_IMAGE_URL)](https://jonbarron.info/mipnerf360/) | - Capture indoor or limited outdoor spaces from the front. Record videos from multiple angles facing forward. Aim for 2~5 minute videos with detailed content. | [Tanks and Temples](https://www.tanksandtemples.org/download/) <br> [Mip-NeRF 360](https://jonbarron.info/mipnerf360/) | CC BY 4.0 |
| Indoor       | [![Dataset Preview](INSERT_IMAGE_URL)](https://github.com/Phog/DeepBlending) | - Capture interior spaces from various angles and heights. If possible, capture the ceiling as well. Avoid capturing entire houses in one go; opt for room-sized data. | [Deep Blending](https://github.com/Phog/DeepBlending) | Apache-2.0 license |


## 👨‍💻 Developer Guide

### 👨‍💻 Run with Docker & GCP
1. Clone this repository.
2. Set up GCP credentials.
3. Build the Docker image:
```
docker build -t MY_CONTAINER_NAME .
```

4. Run the container with volume binding:
```
docker run -d \
   -p 8000:8000 \
   -v $PWD:/app \
   -e ENV_VAR1=VALUE1 \
   -e ENV_VAR2=VALUE2 \
   MY_CONTAINER_NAME
```

## 🔖 References
* MobileNeRF: Exploiting the Polygon Rasterization Pipeline for Efficient Neural Field Rendering on Mobile Architectures (Apache-2.0 license)
* MobileNeRF + WebXR
* HumanNeRF: Free-viewpoint Rendering of Moving Peoplefrom Monocular Video (MIT License)
* Draco (Apache-2.0 license)
