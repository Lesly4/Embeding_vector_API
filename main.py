from fastapi import FastAPI, Request, HTTPException, Body, UploadFile, File
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer, AutoModel
from logging_config import access_logger, error_logger
from typing import Any, List
import pdfplumber
import torch
import io
import asyncio
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ------------------- APP ------------------- #
app = FastAPI(title="Text-to-Vector Embedding API")

# ------------------- MODEL ------------------- #
tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-base")
model = AutoModel.from_pretrained("intfloat/e5-base")
model.eval()

# ------------------- TEXT SPLITTER ------------------- #
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# ------------------- EMBED CHUNK (THREAD SAFE) ------------------- #
async def embed_chunk(chunk: str) -> torch.Tensor:
    loop = asyncio.get_running_loop()

    def sync_embed():
        tokens = tokenizer(chunk, return_tensors="pt", truncation=True)
        with torch.no_grad():
            return model(**tokens).last_hidden_state.mean(dim=1)

    return await loop.run_in_executor(None, sync_embed)

# ------------------- ENDPOINT ------------------- #
@app.post("/convert-text")
async def convert_text(
    request: Request,
    _: Any = Body(None)  # Required for Swagger JSON support
):
    try:
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        text = ""

        # ---------- JSON ----------
        if content_type == "application/json":
            body = await request.json()
            text = body.get("text")
            if not text:
                raise HTTPException(400, "Missing 'text' field")

        # ---------- RAW TEXT ----------
        elif content_type == "text/plain":
            text = (await request.body()).decode("utf-8").strip()
            if not text:
                raise HTTPException(400, "Empty text body")

        # ---------- RAW PDF ----------
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
            raise HTTPException(
                415,
                f"Unsupported Content-Type: {content_type}"
            )

        if not text.strip():
            raise HTTPException(400, "No extractable text found")

        # ---------- SPLIT ----------
        chunks: List[str] = text_splitter.split_text(text)
        if not chunks:
            raise HTTPException(400, "Text could not be split")

        # ---------- PARALLEL EMBEDDING ----------
        embeddings = await asyncio.gather(
            *[embed_chunk(chunk) for chunk in chunks]
        )

        chunk_tensor = torch.vstack(embeddings)
        document_embedding = chunk_tensor.mean(dim=0)

        return {
            "num_chunks": len(chunks),
            "chunk_embedding_shape": tuple(chunk_tensor.shape),
            "document_embedding": document_embedding.tolist()
        }

    # ---------- CLIENT ERRORS ----------
    except HTTPException as e:
        error_logger.warning(
            f"Client error | Path={request.url.path} | "
            f"Status={e.status_code} | Detail={e.detail}"
        )
        raise

    # ---------- SERVER ERRORS ----------
    except Exception as e:
        error_logger.error(
            f"Server error | Path={request.url.path} | Error={str(e)}",
            exc_info=True
        )
        raise HTTPException(500, "Internal server error")

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
        error_logger.error(
            f"Unhandled middleware error | IP={client_ip} | Method={request.method} | "
            f"Path={request.url.path} | Error={str(e)}",
            exc_info=True
        )
        raise

    access_logger.info(
        f"Completed | IP={client_ip} | Method={request.method} | "
        f"Path={request.url.path} | Status={response.status_code}"
    )

    return response

# ------------------- GLOBAL HTTP EXCEPTION ------------------- #
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_logger.warning(
        f"HTTPException | Path={request.url.path} | "
        f"Status={exc.status_code} | Detail={exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

