1. clone this repository

2. GCP Credential

3. Build Docker image: docker build -t MY_CONTAINER_NAME .
// Volume Binding

4. docker run -d \
   -p 8000:8000 \
   -v $PWD:/app \
   -e ENV_VAR1=VALUE1 \
   -e ENV_VAR2=VALUE2 \
   MY_CONTAINER_NAME
