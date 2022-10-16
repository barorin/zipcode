import urllib.parse

import models
from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi_pagination import paginate
from sqlalchemy import and_
from sqlalchemy.orm import Session


def get_all(zipcode: str, address: str, db: Session = Depends(get_db)):
    filters = []
    if zipcode:
        filters.append(models.KenAll.zipcode == zipcode)
    if address:
        decoded_address = urllib.parse.unquote(address)
        filters.append(models.KenAll.address.contains(decoded_address))

    ken_all = (
        db.query(models.KenAll).filter(and_(*filters)).order_by(models.KenAll.id).all()
    )
    if not ken_all:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your query is not available.",
        )

    return paginate(ken_all)
