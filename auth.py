from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from database import SessionLocal
from models import APIKey

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    """
    Validates the API key and returns the APIKey object.
    Raises 401 if invalid.
    """
    key_obj = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not key_obj:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return key_obj

