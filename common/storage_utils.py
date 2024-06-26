from google.cloud import storage
from google.oauth2 import service_account

BUCKET = "3dgs-storage"
KEY_PATH = "../gcp-service-account.json"
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

# !!USAGE BELOW!!
# file = download_from_storage("test/1.jpg")
# print(upload_to_storage("test/1-test.jpg", file, 'image/jpeg'))
    # .png: image/png
    # .json: application/json
    # .glb: model/gltf-binary
    # .fbx: application/octet-stream

# Download from storage and load to memory.
def download_from_storage(file_path: str):
    # Initialize Google Cloud Storage.
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(BUCKET)

    # Download file from Cloud Storage.
    blob = bucket.blob(file_path)
    file_bytes = blob.download_as_bytes()

    return file_bytes

# Upload to storage from memory.
def upload_to_storage(file_path: str, data: bytes, content_type: str):
    # Initialize Google Cloud Storage.
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(BUCKET)

	# Upload file to Cloud Storage.
    blob = bucket.blob(file_path)
    blob.upload_from_string(data, content_type=content_type)

    return {"file_path": file_path}
