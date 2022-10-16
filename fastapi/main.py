from fastapi import FastAPI
from fastapi_pagination import add_pagination
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from database import engine
from models import Base
from routes import index, jigyosyo, ken_all

app = FastAPI()

# slowapi
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ルーティング
app.include_router(index.router)
app.include_router(ken_all.router)
app.include_router(jigyosyo.router)

# テーブル作成
Base.metadata.create_all(engine)

# fastapi-pagination（この位置が大事）
add_pagination(app)
