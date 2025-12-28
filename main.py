from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer, AutoModel
from logging_config import access_logger, error_logger
from typing import Any, List
import pdfplumber
import torch
import io
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================
# CONFIG
# ============================================================

MAX_BODY_SIZE = 15 * 1024 * 1024  # 15 MB (HTTP payload)
MAX_TEXT_SIZE = 15 * 1024 * 1024  # 15 MB (extracted text)

# ============================================================
# APP
# ============================================================

app = FastAPI(title="Text-to-Vector Embedding API")

# ============================================================
# MODEL
# ============================================================

tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-base")
model = AutoModel.from_pretrained("intfloat/e5-base")
model.eval()

# ============================================================
# TEXT SPLITTER
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# ============================================================
# MIDDLEWARE — HARD LIMIT (15 MB)
# ============================================================

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")

    if content_length and int(content_length) > MAX_BODY_SIZE:
        error_logger.warning(
            f"Payload too large | IP={request.client.host if request.client else 'unknown'} "
            f"| Size={content_length} Bytes"
        )
        return JSONResponse(
            status_code=413,
            content={"detail": "Payload too large. Maximum allowed size is 15 MB."}
        )

    return await call_next(request)

# ============================================================
# LOGGING MIDDLEWARE
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    forwarded = request.headers.get("x-forwarded-for")
    client_ip = (
        forwarded.split(",")[0]
        if forwarded
        else (request.client.host if request.client else "unknown")
    )

    api_key = request.headers.get("My-API-Key")

    access_logger.info(
        f"Incoming | IP={client_ip} | Method={request.method} | "
        f"Path={request.url.path} | API_KEY={api_key}"
    )

    try:
        response = await call_next(request)
    except Exception as e:
        error_logger.error(
            f"Unhandled middleware error | IP={client_ip} | "
            f"Path={request.url.path} | Error={str(e)}",
            exc_info=True,
        )
        raise

    access_logger.info(
        f"Completed | IP={client_ip} | Method={request.method} | "
        f"Path={request.url.path} | Status={response.status_code}"
    )

    return response

# ============================================================
# ENDPOINT
# ============================================================

@app.post("/convert-text")
async def convert_text(request: Request, _: Any = Body(None)):
    try:
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        text = ""

        # ---------------- JSON ----------------
        if content_type == "application/json":
            body = await request.json()
            text = body.get("text")
            if not text:
                raise HTTPException(400, "Missing 'text' field")

        # ---------------- TEXT ----------------
        elif content_type == "text/plain":
            raw = await request.body()
            text = raw.decode("utf-8").strip()
            if not text:
                raise HTTPException(400, "Empty text body")

        # ---------------- PDF ----------------
        elif content_type == "application/pdf":
            pdf_bytes = await request.body()
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if not text.strip():
                raise HTTPException(400, "No extractable text found in PDF")

        # ---------------- UNSUPPORTED ----------------
        else:
            raise HTTPException(
                415, f"Unsupported Content-Type: {content_type}"
            )

        # ====================================================
        # TEXT SIZE LIMIT (AFTER EXTRACTION)
        # ====================================================

        if len(text.encode("utf-8")) > MAX_TEXT_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Extracted text exceeds the maximum allowed size of 15 MB",
            )

        # ====================================================
        # SPLIT
        # ====================================================

        chunks: List[str] = text_splitter.split_text(text)
        if not chunks:
            raise HTTPException(400, "Text could not be split into chunks")

        # ====================================================
        #  BATCHED EMBEDDING
        # ====================================================

        tokens = tokenizer(
            chunks,
            return_tensors="pt",
            padding=True,
            truncation=False,
            max_length=512
        )

        with torch.no_grad():
            chunk_embeddings = model(**tokens).last_hidden_state.mean(dim=1)

        document_embedding = chunk_embeddings.mean(dim=0)

        return {
            "num_chunks": len(chunks),
            "chunk_embedding_shape": tuple(chunk_embeddings.shape),
            "document_embedding": document_embedding.tolist(),
        }

    # ---------------- CLIENT ERRORS ----------------
    except HTTPException as e:
        error_logger.warning(
            f"Client error | Path={request.url.path} | "
            f"Status={e.status_code} | Detail={e.detail}"
        )
        raise

    # ---------------- SERVER ERRORS ----------------
    except Exception as e:
        error_logger.error(
            f"Server error | Path={request.url.path} | Error={str(e)}",
            exc_info=True,
        )
        raise HTTPException(500, "Internal server error")

# ============================================================
# GLOBAL HTTP EXCEPTION HANDLER
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_logger.warning(
        f"HTTPException | Path={request.url.path} | "
        f"Status={exc.status_code} | Detail={exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

