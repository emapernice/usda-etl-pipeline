from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/summary")
def get_price_summary(db: Session = Depends(get_db)):
    """
    Returns average, minimum, and maximum prices grouped by commodity.
    """
    try:
        sql = text("""
            SELECT 
                commodity_desc,
                COUNT(*) AS records,
                ROUND(AVG(price), 2) AS avg_price,
                ROUND(MIN(price), 2) AS min_price,
                ROUND(MAX(price), 2) AS max_price
            FROM usda_observations
            GROUP BY commodity_desc
            ORDER BY avg_price DESC
        """)

        result = db.execute(sql).mappings().all()
        return {"count": len(result), "data": [dict(r) for r in result]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.get("/average")
def get_average_price(
    year: int | None = Query(None, description="Filter by year"),
    state: str | None = Query(None, description="Filter by state abbreviation (e.g., IA)"),
    commodity: str | None = Query(None, description="Filter by commodity name (e.g., SOYBEANS)"),
    db: Session = Depends(get_db),
):
    """
    Returns the average price optionally filtered by year, state, or commodity.
    Examples:
      /stats/average?year=2023
      /stats/average?state=IA
      /stats/average?commodity=CORN
      /stats/average?year=2023&state=IA&commodity=SOYBEANS
    """
    try:
        where_clauses = []
        params = {}

        if year:
            where_clauses.append("year = :year")
            params["year"] = year
        if state:
            where_clauses.append("state_name = :state")
            params["state"] = state.upper()
        if commodity:
            where_clauses.append("commodity_desc = :commodity")
            params["commodity"] = commodity.upper()

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        sql = text(f"""
            SELECT 
                COUNT(*) AS records,
                ROUND(AVG(price), 2) AS avg_price,
                ROUND(MIN(price), 2) AS min_price,
                ROUND(MAX(price), 2) AS max_price
            FROM usda_observations
            {where_sql}
        """)

        result = db.execute(sql, params).mappings().first()

        if not result or result["records"] == 0:
            raise HTTPException(status_code=404, detail="No data found for given filters")

        return {
            "filters": {k: v for k, v in params.items()},
            "stats": dict(result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
