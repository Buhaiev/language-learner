import os

from openai import OpenAI
from pydantic import BaseModel

class TranslationResponse(BaseModel):
    detailed_translation: str
    concise_translation: str

def setup_ai_client():
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        return None

    try:
        return OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
    except Exception as e:
        print(f"Error setting up AI client: {e}")
        raise RuntimeError("Failed to set up AI client") from e
