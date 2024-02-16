FROM dromni/nerfstudio:0.3.4
RUN pip install "jax[cuda11_cudnn86]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

USER root
RUN apt-get update && apt-get install -y 
RUN apt-get install -y libgl1-mesa-dev
RUN apt-get install -y libglib2.0-0

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]