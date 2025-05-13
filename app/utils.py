import jwt
import base64
import bcrypt
import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import RefreshToken

SECRET_KEY = "your_secret_key_here"

def generate_access_token(user_guid: str, user_ip: str):
    payload = {
        "user_guid": str(user_guid),
        "user_ip": user_ip,
        "token_id": secrets.token_hex(16), 
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS512")

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS512"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_refresh_token():
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")

def hash_refresh_token(token: str):
    return bcrypt.hashpw(token.encode("utf-8"), bcrypt.gensalt())

def verify_refresh_token(stored_hash: bytes, provided_token: str):
    return bcrypt.checkpw(provided_token.encode("utf-8"), stored_hash)
# def verify_refresh_token(stored_hash: str, provided_token: str):
#     return bcrypt.checkpw(provided_token.encode("utf-8"), stored_hash.encode("utf-8"))

def send_email_warning(user_guid: str):
    print(f"WARNING: IP address changed for user {user_guid}. Email sent.")