from typing import Optional

import schemas
from config import Setting
from database import get_db
from fastapi import APIRouter, Depends, Request, status
from fastapi_pagination import Page
from functions import jigyosyo
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

settings = Setting()

router = APIRouter(prefix=f"/{settings.version}/jigyosyo", tags=["jigyosyo"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas.Jigyosyo],
)
@limiter.limit("5/minute")
def get_jigyosyo(
    request: Request,  # slowapi用
    zipcode: Optional[str] = None,
    address: Optional[str] = None,
    compnay_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return jigyosyo.get_all(zipcode, address, compnay_name, db)
