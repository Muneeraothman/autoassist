import json
import os

import boto3
from dotenv import load_dotenv

from models import EMBEDDING_DIMENSIONS

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Unlike Claude Sonnet 4.5, Titan Text Embeddings V2 IS available in-region
# in us-east-1 - no cross-region inference profile needed for this one.
TITAN_EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"

bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def embed_text(text: str) -> list[float]:
    response = bedrock_runtime.invoke_model(
        modelId=TITAN_EMBED_MODEL_ID,
        body=json.dumps(
            {
                "inputText": text,
                "dimensions": EMBEDDING_DIMENSIONS,
                "normalize": True,
            }
        ),
    )
    return json.loads(response["body"].read())["embedding"]
