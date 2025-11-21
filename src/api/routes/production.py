from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..db import get_db

router = APIRouter()

@router.get("/")
def get_production_report(db: Session = Depends(get_db)):
    """
    Returns all records where statisticcat_desc = 'PRODUCTION'.
    Response: {"count": <n>, "data": [...]}
    """
    query = text("""
        SELECT year, state_name, commodity_desc, value, unit_desc
        FROM usda_observations
        WHERE statisticcat_desc = 'PRODUCTION'
        ORDER BY year DESC, state_name;
    """)

    rows = db.execute(query).mappings().all()
    return {"count": len(rows), "data": [dict(r) for r in rows]}
