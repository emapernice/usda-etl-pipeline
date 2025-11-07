from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health_check(db: Session = Depends(get_db)):
    """
    Returns API and database connection health status.
    """
    try:
        result = db.execute(text("SELECT NOW() AS db_time"))
        db_time = result.scalar()
        return {
            "status": "ok",
            "database": "connected",
            "db_time": str(db_time)
        }
    except Exception as e:
        return {"status": "error", "database": str(e)}
