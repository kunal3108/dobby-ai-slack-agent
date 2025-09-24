import boto3
import json

def load_secrets(secret_name="dobby-ai-secrets", region="ap-south-1"):
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    secrets = json.loads(response["SecretString"])
    return secrets
