from fastapi import FastAPI, Request, HTTPException, Body
from transformers import AutoTokenizer, AutoModel
from logging_config import logger
from typing import Any
import pdfplumber
import torch
import io


app = FastAPI(title="Text-to-Vector Embedding API")

tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-base")
model = AutoModel.from_pretrained("intfloat/e5-base")


@app.post("/convert-text")
async def convert_text(
    request: Request,
    _: Any = Body(None)  # ← REQUIRED for Swagger / JSON
):
    try:
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            body = await request.json()
            text = body.get("text")
            if not text:
                raise HTTPException(400, "Missing 'text' field")

        elif "text/plain" in content_type:
            text = (await request.body()).decode("utf-8")

        elif "application/pdf" in content_type:
            pdf_bytes = await request.body()
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        text += page.extract_text() + "\n"

            if not text.strip():
                raise HTTPException(400, "No extractable text in PDF")

        else:
            raise HTTPException(415, f"Unsupported Content-Type: {content_type}")

        tokens = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            vector = model(**tokens).last_hidden_state.mean(dim=1)

        return {
            "text_length": len(text),
            "vector_shape": tuple(vector.shape),
            "embedding": vector.tolist()[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

# ------------------- Middleware ------------------- #
@app.middleware("http")
async def log_requests(request: Request, call_next):
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else request.client.host

    api_key = request.headers.get("My-API-Key")

    logger.info(
        f"Incoming request | ClientIP={client_ip} | Method={request.method} | Endpoint={request.url.path} | API_KEY={api_key}"
    )

    response = await call_next(request)

    logger.info(
        f"Completed request | ClientIP={client_ip} | Method={request.method} | Endpoint={request.url.path} | Status={response.status_code} | API_KEY={api_key}"
    )

    return response

