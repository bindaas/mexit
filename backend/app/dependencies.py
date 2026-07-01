import json
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User

_firebase_initialized = False


def _ensure_firebase_initialized() -> None:
    global _firebase_initialized
    if _firebase_initialized:
        return
    import firebase_admin
    from firebase_admin import credentials

    if not firebase_admin._apps:
        if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            cred = credentials.Certificate(json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON))
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    _firebase_initialized = True


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-ID"),
    db: Session = Depends(get_db),
) -> str:
    if settings.TEST_AUTH_BYPASS:
        if not x_user_id:
            raise HTTPException(status_code=401, detail="X-User-ID header required")
        user = db.query(User).filter(User.id == x_user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Unknown user")
        return user.id

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    _ensure_firebase_initialized()
    from firebase_admin import auth as firebase_auth

    token = authorization.removeprefix("Bearer ")
    try:
        decoded = firebase_auth.verify_id_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = db.query(User).filter(User.firebase_uid == decoded["uid"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Unknown user")
    return user.id
