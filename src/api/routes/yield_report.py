from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import get_db

router = APIRouter()

@router.get("/")
def get_yield_report(db: Session = Depends(get_db)):
    query = text("""
        SELECT year, state_name, commodity_desc, value, unit_desc
        FROM usda_observations
        WHERE statisticcat_desc = 'YIELD'
        ORDER BY year DESC, state_name;
    """)

    result = db.execute(query).fetchall()

    return [
        {
            "year": row.year,
            "state_name": row.state_name,
            "commodity_desc": row.commodity_desc,
            "value": row.value,
            "unit_desc": row.unit_desc,
        }
        for row in result
    ]
