FROM dromni/nerfstudio:1.0.2

USER root
WORKDIR /app
COPY ./requirements.txt /app/
COPY ./libs/pixel-perfect-sfm/pixsfm/features/extractor.py /home/user/pixel-perfect-sfm/pixsfm/features/extractor.py
COPY . /app


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="/home/user/nerfstudio:${PATH}"
ENV PATH="/home/user/.local/bin:${PATH}"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]