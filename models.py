from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, nullable=True)  # remove ForeignKey
    endpoint = Column(String)
    method = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    client_ip = Column(String)

