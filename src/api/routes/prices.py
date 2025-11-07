from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get("/")
def get_prices(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    commodity: str | None = Query(None),
    state: str | None = Query(None),
    year: int | None = Query(None),
    db: Session = Depends(get_db),
):

    try:
        where_clauses = []
        params = {}

        if commodity:
            where_clauses.append("commodity_desc = :commodity")
            params["commodity"] = commodity.upper()

        if state:
            where_clauses.append("state_name = :state")
            params["state"] = state.upper()

        if year:
            where_clauses.append("year = :year")
            params["year"] = year

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        sql = text(f"""
            SELECT year, state_name, commodity_desc, price
            FROM usda_observations
            {where_sql}
            ORDER BY year DESC
            LIMIT :limit OFFSET :offset
        """)

        params["limit"] = limit
        params["offset"] = offset

        result = db.execute(sql, params)

        rows = result.mappings().all()
        data = [dict(r) for r in rows]

        return {"count": len(data), "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
