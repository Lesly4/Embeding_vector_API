from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch
from database import Base, engine
from logging_config import logger

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Text-to-Vector Embedding API")

# Load tokenizer and model once
tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-base")
model = AutoModel.from_pretrained("intfloat/e5-base")


class TextInput(BaseModel):
    text: str


# ------------------- API Endpoint ------------------- #
@app.post("/convert-text")
def convert_text(input_data: TextInput, request: Request):
    try:
        tokens = tokenizer(input_data.text, return_tensors="pt")
        with torch.no_grad():
            vector = model(**tokens).last_hidden_state.mean(dim=1)

        return {
            "Your text": input_data.text,
            "The resulting vector shape is": tuple(vector.shape),
            "Embedding-Vector": vector.tolist()[0]
        }
    except Exception as e:
        return {"error": str(e)}


# ------------------- Middleware ------------------- #
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Extract client IP (supports X-Forwarded-For if behind a proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else request.client.host

    # Extract API key if provided
    api_key = request.headers.get("My-API-Key")

    # Log incoming request
    logger.info(
        f"Incoming request | ClientIP={client_ip} | Method={request.method} | Endpoint={request.url.path} | API_KEY={api_key}"
    )

    response = await call_next(request)

    # Log completed request
    logger.info(
        f"Completed request | ClientIP={client_ip} | Method={request.method} | Endpoint={request.url.path} | Status={response.status_code} | API_KEY={api_key}"
    )

    return response

