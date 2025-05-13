from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import SessionLocal, engine
from fastapi import Query
from uuid import UUID
import uuid


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tokens", response_model=schemas.TokenResponse)
def gen_token(user_guid: UUID = Query(...), db: Session = Depends(get_db)):
    '''Вызов функции для генерации токенов для юзера по гуид'''
    user_ip = "127.0.0.1" # ip для упрощения одинаковый везде
    access_token = utils.generate_access_token(user_guid, user_ip)
    refresh_token = utils.generate_refresh_token()
    refresh_token_hash = utils.hash_refresh_token(refresh_token)

    token_record = models.RefreshToken(
        user_guid=str(user_guid),
        token_hash=refresh_token_hash,
        access_token_id=utils.decode_access_token(access_token)["token_id"],
        user_ip=user_ip
    )
    db.add(token_record)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token}

@app.post("/refresh", response_model=schemas.TokenResponse)
def refresh_tokens(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    '''Рефрешим токены для юзера по гуид и рефрештокену'''
    user_ip = "127.0.0.1"
    stored_token = db.query(models.RefreshToken).filter_by(user_guid=str(request.user_guid)).first()

    if not stored_token or not utils.verify_refresh_token(stored_token.token_hash, request.refresh_token):
        raise HTTPException(status_code=401, detail="Invalid refresh token" +stored_token.token_hash+'rea'+ request.refresh_token )

    if stored_token.user_ip != user_ip:
        utils.send_email_warning(request.user_guid)

    new_access_token = utils.generate_access_token(request.user_guid, user_ip)
    new_refresh_token = utils.generate_refresh_token()
    new_refresh_token_hash = utils.hash_refresh_token(new_refresh_token)

    stored_token.token_hash = new_refresh_token_hash
    stored_token.access_token_id = utils.decode_access_token(new_access_token)["token_id"]
    stored_token.user_ip = user_ip
    db.commit()

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}

@app.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.RefreshToken).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

@app.get("/gener_guid")
def gener_guid():
    uiid_gener = uuid.uuid4()
    return {"message": uiid_gener}