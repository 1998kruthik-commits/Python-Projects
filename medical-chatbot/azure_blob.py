import os
from azure.storage.blob import BlobServiceClient

# Read connection string from environment variable
from keyvault import storage_connection_string

blob_service = BlobServiceClient.from_connection_string(
    storage_connection_string
)

if not CONNECTION_STRING:
    raise Exception(
        "AZURE_STORAGE_CONNECTION_STRING environment variable is not set."
    )

blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)


def download_files(container_name, files):

    container = blob_service.get_container_client(container_name)

    for blob_name, local_path in files.items():

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        if os.path.exists(local_path):
            print(f"{local_path} already exists.")
            continue

        print(f"Downloading {blob_name}...")

        blob = container.get_blob_client(blob_name)

        with open(local_path, "wb") as f:
            f.write(blob.download_blob().readall())

    print("All files downloaded successfully.")
