import boto3
import json
import os

def load_secrets(secret_name="dobby-ai-slack-agent-secrets", region="ap-south-1"):
    """
    Load secrets from AWS Secrets Manager.
    Falls back to environment variables if local dev.
    """
    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response["SecretString"])

        # Export into os.environ for compatibility
        for key, val in secret_dict.items():
            os.environ[key] = val

        return secret_dict
    except Exception as e:
        print(f"⚠️ Failed to load secrets from AWS: {e}")
        return {}
