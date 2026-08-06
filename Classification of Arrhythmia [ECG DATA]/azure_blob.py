import os
from azure.storage.blob import BlobServiceClient

from keyvault import storage_connection_string

blob_service = BlobServiceClient.from_connection_string(
    storage_connection_string
)

if CONNECTION_STRING is None:
    raise Exception("AZURE_STORAGE_CONNECTION_STRING environment variable not found.")

blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

CONTAINER_NAME = "arrhythmia-files"


def download_arrhythmia_files():

    files = {
        "arrhythmia_model.pkl": "models/arrhythmia_model.pkl",
        "imputer.pkl": "models/imputer.pkl",
        "arrhythmia.csv": "data/arrhythmia.csv"
    }

    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    for blob_name, local_path in files.items():

        if os.path.exists(local_path):
            print(f"{local_path} already exists.")
            continue

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        print(f"Downloading {blob_name}...")

        blob_client = container_client.get_blob_client(blob_name)

        with open(local_path, "wb") as file:
            file.write(blob_client.download_blob().readall())

    print("All Arrhythmia files downloaded successfully.")
