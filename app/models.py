from sqlalchemy import Column, String
from .database import Base
import bcrypt

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    user_guid = Column(String(36), primary_key=True, index=True)  # GUID пользователя
    token_hash = Column(String(128), nullable=False)  # хэш refresh токена
    access_token_id = Column(String(255), nullable=False)  # ID связанного access токена
    user_ip = Column(String(45), nullable=False)  # IP адрес клиента