from google.cloud import firestore
from google.oauth2 import service_account

KEY_PATH = "../gcp-service-account.json"
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

def is_sample(id: str):
    COLLECTION = "request_info"
    data = firestore.Client(credentials=credentials).collection(COLLECTION).document(id).get().to_dict()
    return data['isSample']

class VRData:
    VR_RESOURCE_COLLECTION = "vr_resource"
    REQUEST_COLLECTION = "3dgs_request"

    def __init__(self):
        self.db = firestore.Client(credentials=credentials)

    def insert_vr_resource(self, id: str, title: str, type: str, groupId: str, filePath: str):
        data = {
            "id": id,
            "title": title,
            "type": type,
            "groupId": groupId,
            "filePath": filePath,
            "createdAt": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = self.db.collection(self.VR_RESOURCE_COLLECTION).document(id)
        doc_ref.set(data)

        return {"doc_id": doc_ref.id}

    def get_request(self, doc_id: str):
        doc_ref = self.db.collection(self.REQUEST_COLLECTION).document(doc_id)
        doc = doc_ref.get()

        return doc.to_dict()

    def update_request_status(self, doc_id: str, status: str):
        if status not in ['pending', 'processing', 'completed', 'failed']:
            raise ValueError("Invalid status. Must be 'pending', 'processing', 'completed', or 'failed'.")
        
        doc_ref = self.db.collection(self.REQUEST_COLLECTION).document(doc_id)
        doc_ref.update({"status": status})

        return {"doc_id": doc_id, "status": status}

    def update_request_status_completed(self, doc_id: str):
        return self.update_request_status(doc_id, 'completed')

    def update_request_status_failed(self, doc_id: str):
        return self.update_request_status(doc_id, 'failed')

    def update_request_status_processing(self, doc_id: str):
        return self.update_request_status(doc_id, 'processing')

class SampleVRData:
    VR_RESOURCE_COLLECTION = "sample_response"
    REQUEST_COLLECTION = "sample_request"

    def __init__(self):
        self.db = firestore.Client(credentials=credentials)

    def insert_vr_resource(self, id: str, title: str, type: str, filePath: str):
        data = {
            "id": id,
            "title": title,
            "type": type,
            "filePath": filePath,
            "createdAt": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = self.db.collection(self.VR_RESOURCE_COLLECTION).document(id)
        doc_ref.set(data)

        return {"doc_id": doc_ref.id}

    def get_request(self, doc_id: str):
        doc_ref = self.db.collection(self.REQUEST_COLLECTION).document(doc_id)
        doc = doc_ref.get()

        return doc.to_dict()

    def update_request_status(self, doc_id: str, status: str):
        if status not in ['pending', 'processing', 'completed', 'failed']:
            raise ValueError("Invalid status. Must be 'pending', 'processing', 'completed', or 'failed'.")
        
        doc_ref = self.db.collection(self.REQUEST_COLLECTION).document(doc_id)
        doc_ref.update({"status": status})

        return {"doc_id": doc_id, "status": status}

    def update_request_status_completed(self, doc_id: str):
        return self.update_request_status(doc_id, 'completed')

    def update_request_status_failed(self, doc_id: str):
        return self.update_request_status(doc_id, 'failed')

    def update_request_status_processing(self, doc_id: str):
        return self.update_request_status(doc_id, 'processing')