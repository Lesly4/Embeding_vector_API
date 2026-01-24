from database import engine
from models import APIKey, RequestLog
from sqlalchemy.orm import Session

session = Session(bind=engine)

print("API Keys:")
for key in session.query(APIKey).all():
    print(key.id, key.key, key.owner)

print("\nLogs:")
for log in session.query(RequestLog).all():
    print(log.id, log.api_key_id, log.endpoint, log.timestamp)

