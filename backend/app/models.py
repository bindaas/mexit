import uuid

from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000001"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
