from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.schemas import HealthCheck

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API and database connectivity
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        database=db_status,
        version="1.0.0"
    )
