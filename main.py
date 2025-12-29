from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer, AutoModel
from logging_config import access_logger, error_logger
from typing import Any, List
import pdfplumber
import torch
import io
import tempfile
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdf_chunker_for_rag import CleanHybridPDFChunker

# ============================================================
# CONFIG
# ============================================================

MAX_BODY_SIZE = 15 * 1024 * 1024  # 15 MB
MAX_TEXT_SIZE = 15 * 1024 * 1024  # 15 MB

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
# CHUNKERS
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

pdf_chunker = CleanHybridPDFChunker()

# ============================================================
# MIDDLEWARE — HARD LIMIT
# ============================================================

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(
            status_code=413,
            content={"detail": "Payload too large. Max 15 MB."}
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
# EMBEDDING FUNCTION
# ============================================================

def embed_chunks(chunks: List[str]) -> torch.Tensor:
    tokens = tokenizer(
        chunks,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    )
    with torch.no_grad():
        chunk_embeddings = model(**tokens).last_hidden_state.mean(dim=1)
    return chunk_embeddings

# ============================================================
# ENDPOINT
# ============================================================

@app.post("/convert-text")
async def convert_text(request: Request, _: Any = Body(None)):
    try:
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        chunks: List[str] = []
        chunk_metadata = []

        # ---------------- JSON ----------------
        if content_type == "application/json":
            body = await request.json()
            text = body.get("text")
            if not text:
                raise HTTPException(400, "Missing 'text'")
            text = text.strip() 
            chunks = text_splitter.split_text(text)

        # ---------------- TEXT ----------------
        elif content_type == "text/plain":
            raw = await request.body()
            try:
                text = raw.decode("utf-8").strip()
            except UnicodeDecodeError:
                raise HTTPException(400, "Invalid UTF-8 text encoding")
            if not text:
                raise HTTPException(400, "Empty body")
            chunks = text_splitter.split_text(text)

        # ---------------- PDF ----------------
        elif content_type == "application/pdf":
            pdf_bytes = await request.body()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_bytes)
                pdf_path = tmp.name

            try:
                structured_chunks = pdf_chunker.strategic_header_chunking(
                    pdf_path=pdf_path,
                    target_words_per_chunk=1000
                )

                for group in structured_chunks:
                    for chunk in group:
                        text = chunk.get("text", "").strip()
                        if text:
                            chunks.append(text)
                            chunk_metadata.append({
                                "page": chunk.get("page"),
                                "header": chunk.get("header"),
                            })
            finally:
                os.remove(pdf_path)

            if not chunks:
                raise HTTPException(400, "No extractable text found in PDF")

        # ---------------- UNSUPPORTED ----------------
        else:
            raise HTTPException(415, f"Unsupported Content-Type: {content_type}")

        # ====================================================
        # TEXT SIZE LIMIT
        # ====================================================

        total_bytes = sum(len(c.encode("utf-8")) for c in chunks)
        if total_bytes > MAX_TEXT_SIZE:
            raise HTTPException(413, "Extracted text exceeds 15 MB")

        # ====================================================
        # BATCHED EMBEDDING
        # ====================================================

        chunk_embeddings = embed_chunks(chunks)

        # ====================================================
        # MAP RESULTS
        # ====================================================

        results = [
            {
                "Chunk_index": i,
                "Text": chunk,
                "Number_characters": len(chunk),
                "Number_bytes": len(chunk.encode("utf-8")),
                "Metadata": meta,
                "Embedding": emb.tolist(),
            }
            for i, (chunk, emb, meta) in enumerate(
                zip(chunks, chunk_embeddings, chunk_metadata + [None]*len(chunks))
            )
        ]

        return {
            "Number_chunks": len(results),
            "Embedding_dim": chunk_embeddings.shape[1],
            "Chunks": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        error_logger.error(str(e), exc_info=True)
        raise HTTPException(500, "Internal server error")

# ============================================================
# GLOBAL HTTP EXCEPTION HANDLER
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

