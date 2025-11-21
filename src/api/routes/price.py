from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..db import get_db

router = APIRouter()

@router.get("/")
def get_price_report(db: Session = Depends(get_db)):
    """
    Returns all records where statisticcat_desc = 'PRICE RECEIVED'.
    Response: {"count": <n>, "data": [ {year, state_name, commodity_desc, value, unit_desc}, ... ]}
    """
    query = text("""
        SELECT year, state_name, commodity_desc, value, unit_desc
        FROM usda_observations
        WHERE statisticcat_desc = 'PRICE RECEIVED'
        ORDER BY year DESC, state_name;
    """)

    rows = db.execute(query).mappings().all()
    return {"count": len(rows), "data": [dict(r) for r in rows]}
