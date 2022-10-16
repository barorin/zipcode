from sqlalchemy import Column, Integer, String

from database import Base


class KenAll(Base):
    __tablename__ = "ken_all"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    zipcode = Column(String)
    prefecture = Column(String)
    city = Column(String)
    town = Column(String)
    address = Column(String)


class Jigyosyo(Base):
    __tablename__ = "jigyosyo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company = Column(String)
    zipcode = Column(String)
    prefecture = Column(String)
    city = Column(String)
    town = Column(String)
    chome = Column(String)
    address = Column(String)
