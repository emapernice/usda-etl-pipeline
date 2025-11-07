from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix="/prices", tags=["Prices"])


def get_pagination_metadata(total_records: int, limit: int, offset: int):
    current_page = (offset // limit) + 1
    total_pages = (total_records + limit - 1) // limit
    return {
        "page": current_page,
        "page_size": limit,
        "total_records": total_records,
        "total_pages": total_pages
    }


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

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Count total records
        count_sql = text(f"SELECT COUNT(*) FROM usda_observations {where_sql}")
        total_records = db.execute(count_sql, params).scalar()

        # Fetch paginated results
        sql = text(f"""
            SELECT year, state_name, commodity_desc, price
            FROM usda_observations
            {where_sql}
            ORDER BY year DESC
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = limit
        params["offset"] = offset

        rows = db.execute(sql, params).mappings().all()
        data = [dict(r) for r in rows]

        metadata = get_pagination_metadata(total_records, limit, offset)

        return {"metadata": metadata, "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.get("/state/{state}")
def get_prices_by_state(
    state: str,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        sql = text("""
            SELECT year, state_name, commodity_desc, price
            FROM usda_observations
            WHERE state_name = :state
            ORDER BY year DESC
            LIMIT :limit OFFSET :offset
        """)
        params = {"state": state.upper(), "limit": limit, "offset": offset}

        total_records = db.execute(
            text("SELECT COUNT(*) FROM usda_observations WHERE state_name = :state"), {"state": state.upper()}
        ).scalar()

        rows = db.execute(sql, params).mappings().all()
        metadata = get_pagination_metadata(total_records, limit, offset)

        return {"metadata": metadata, "data": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.get("/commodity/{commodity}")
def get_prices_by_commodity(
    commodity: str,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        sql = text("""
            SELECT year, state_name, commodity_desc, price
            FROM usda_observations
            WHERE commodity_desc = :commodity
            ORDER BY year DESC
            LIMIT :limit OFFSET :offset
        """)
        params = {"commodity": commodity.upper(), "limit": limit, "offset": offset}

        total_records = db.execute(
            text("SELECT COUNT(*) FROM usda_observations WHERE commodity_desc = :commodity"),
            {"commodity": commodity.upper()},
        ).scalar()

        rows = db.execute(sql, params).mappings().all()
        metadata = get_pagination_metadata(total_records, limit, offset)

        return {"metadata": metadata, "data": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
