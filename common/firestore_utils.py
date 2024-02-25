from google.cloud import firestore
from config import VR_RESOURCE_COLLECTION, REQUEST_COLLECTION

# Insert generated VR resource(avatar, scene) data,
# when the task successfully finished.
def insert_vr_resource(id: str, title: str, type:str, groupId: str, filePath: str):
    data: dict = {
        "id": id, # same as get_request
        "title": title, # same as get_request
        "type": type, # same as get_request
        "groupId": groupId, # same as get_request
        "filePath": filePath, # generated file's path
        "createdAt": firestore.SERVER_TIMESTAMP
    }
    db = firestore.Client()

    doc_ref = db.collection(VR_RESOURCE_COLLECTION).document(id)
    doc_ref.set(data)

    return {"doc_id": doc_ref.id}

# Get request data,
# when server starts the task.
def get_request(doc_id: str):
    db = firestore.Client()

    doc_ref = db.collection(REQUEST_COLLECTION).document(doc_id)
    doc = doc_ref.get()

    return doc.to_dict()

# Update request's status,
# when the task has finished.
def update_request_status_completed(doc_id: str):
    return update_request_status(doc_id, 'completed')

# when the task has failed.
def update_request_status_failed(doc_id: str):
    return update_request_status(doc_id, 'failed')

# when the task has started.
def update_request_status_processing(doc_id: str):
    return update_request_status(doc_id, 'processing')

# status must be in 'pending' | 'processing' | 'completed' | 'failed'.
def update_request_status(doc_id: str, status: str):
    db = firestore.Client()

    doc_ref = db.collection(REQUEST_COLLECTION).document(doc_id)
    doc_ref.update({"status": status})

    return {"doc_id": doc_id, "status": status}
