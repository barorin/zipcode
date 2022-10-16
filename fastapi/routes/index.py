from config import Setting
from fastapi import APIRouter, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

settings = Setting()

router = APIRouter(tags=["index"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def index(request: Request):  # slowapi用
    return {"info": "pleaase access /docs"}
