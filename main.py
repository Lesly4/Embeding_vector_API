from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer, AutoModel
from logging_config import access_logger, error_logger
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
    _: Any = Body(None)  # Required for Swagger JSON support
):
    try:
        # Normalize Content-Type
        content_type = request.headers.get("content-type", "").split(";")[0].strip()

        # ---------- JSON ----------
        if content_type == "application/json":
            body = await request.json()
            text = body.get("text")
            if not text:
                raise HTTPException(status_code=400, detail="Missing 'text' field")

        # ---------- RAW TEXT ----------
        elif content_type == "text/plain":
            text = (await request.body()).decode("utf-8").strip()
            if not text:
                raise HTTPException(status_code=400, detail="Empty text body")

        # ---------- PDF ----------
        elif content_type == "application/pdf":
            pdf_bytes = await request.body()
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if not text.strip():
                raise HTTPException(status_code=400, detail="No extractable text found in PDF")

        # ---------- UNSUPPORTED ----------
        else:
            raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {content_type}")

        # ---------- EMBEDDING ----------
        tokens = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            vector = model(**tokens).last_hidden_state.mean(dim=1)

        return {
            "text_length": len(text),
            "vector_shape": tuple(vector.shape),
            "embedding": vector.tolist()[0]
        }

    except HTTPException as e:
        # Log all client errors
        error_logger.warning(
            f"Client error | Path={request.url.path} | Status={e.status_code} | Detail={e.detail}"
        )
        raise

    except Exception as e:
        # Log all server errors
        error_logger.error(
            f"Server error | Path={request.url.path} | Error={str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ------------------- MIDDLEWARE ------------------- #
@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    api_key = request.headers.get("My-API-Key")

    access_logger.info(
        f"Incoming | IP={client_ip} | Method={request.method} | "
        f"Path={request.url.path} | API_KEY={api_key}"
    )

    try:
        response = await call_next(request)
    except Exception as e:
        # Middleware catches errors not handled in routes
        error_logger.error(
            f"Unhandled middleware error | IP={client_ip} | Method={request.method} | "
            f"Path={request.url.path} | API_KEY={api_key} | Error={str(e)}",
            exc_info=True
        )
        raise

    access_logger.info(
        f"Completed | IP={client_ip} | Method={request.method} | "
        f"Path={request.url.path} | Status={response.status_code} | API_KEY={api_key}"
    )

    return response


# ------------------- GLOBAL EXCEPTION HANDLER ------------------- #
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Log any HTTPExceptions not caught in route
    error_logger.warning(
        f"Global HTTPException | Path={request.url.path} | Status={exc.status_code} | Detail={exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

