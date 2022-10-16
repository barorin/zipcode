import urllib.parse

import models
from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi_pagination import paginate
from sqlalchemy import and_
from sqlalchemy.orm import Session


def get_all(
    zipcode: str,
    address: str,
    company_name: str,
    db: Session = Depends(get_db),
):
    filters = []
    if zipcode:
        filters.append(models.Jigyosyo.zipcode == zipcode)
    if address:
        decoded_address = urllib.parse.unquote(address)
        filters.append(models.Jigyosyo.address.contains(decoded_address))
    if company_name:
        decoded_company_name = urllib.parse.unquote(company_name)
        filters.append(models.Jigyosyo.company.contains(decoded_company_name))

    jigyosyo = (
        db.query(models.Jigyosyo)
        .filter(and_(*filters))
        .order_by(models.Jigyosyo.id)
        .all()
    )
    if not jigyosyo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your query is not available.",
        )

    return paginate(jigyosyo)
