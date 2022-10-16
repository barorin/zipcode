from pydantic import BaseSettings


class Setting(BaseSettings):
    version: str = "v1"
