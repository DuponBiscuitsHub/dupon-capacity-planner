from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

# Initialize FastAPI application
app = FastAPI(
    title="Dupon Capacity Planner API",
    description="Operations analytical backend for the Dupon Capacity Planner (DCP).",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """
    Root endpoint returning general API metadata.
    """
    return {
        "status": "online",
        "app": "Dupon Capacity Planner Backend",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connectivity.
    """
    try:
        # Perform a lightweight query to ensure database connection pooling works
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "detail": str(e)
        }
