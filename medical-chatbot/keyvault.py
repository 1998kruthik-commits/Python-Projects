from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

KEYVAULT_URL = "https://mlproject-keyvault.vault.azure.net/"

credential = DefaultAzureCredential()

client = SecretClient(
    vault_url=KEYVAULT_URL,
    credential=credential
)

storage_key = client.get_secret("storage-connection-string").value
