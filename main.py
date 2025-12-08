from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch
from logger import log_request
from database import Base, engine
from logging_config import logger

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Load tokenizer and model once
tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-base")
model = AutoModel.from_pretrained("intfloat/e5-base")

class TextInput(BaseModel):
    text: str

@app.post("/convert-text")
def convert_text(input_data: TextInput, request: Request):
    try:
        log_request(request)
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_ip = request.client.host
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else request.client.host
    logger.info(f"Incoming request from {client_ip}: {request.method} {request.url}")

    response = await call_next(request)

    logger.info(
        f"Completed request from {client_ip}: {request.method} {request.url} - Status {response.status_code}"
    )

    return response

