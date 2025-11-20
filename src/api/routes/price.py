from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db

router = APIRouter()

@router.get("/")
def get_price_report(db: Session = Depends(get_db)):
    query = """
        SELECT year, state_name, commodity_desc, value, unit_desc
        FROM usda_observations
        WHERE statisticcat_desc = 'PRICE RECEIVED'
        ORDER BY year DESC, state_name;
    """
    result = db.execute(query).fetchall()
    return result
