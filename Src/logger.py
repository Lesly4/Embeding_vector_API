from models import RequestLog
from database import SessionLocal
from datetime import datetime
from fastapi import Request

def log_request(request: Request, api_key_id: int = None):
    """
    Logs each API request to the database.
    - request: FastAPI Request object
    - api_key_id: optional (here None)
    """
    db = SessionLocal()
    try:
        log = RequestLog(
            api_key_id=api_key_id,
            endpoint=request.url.path,
            method=request.method,
            timestamp=datetime.utcnow(),
            client_ip=request.client.host
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

