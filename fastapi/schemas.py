from pydantic import BaseModel


class KenAll(BaseModel):
    zipcode: str
    # prefecture: str
    # city: str
    # town: str
    address: str

    class Config:
        orm_mode = True


class Jigyosyo(BaseModel):
    company: str
    zipcode: str
    # prefecture: str
    # city: str
    # town: str
    # chome: str
    address: str

    class Config:
        orm_mode = True
