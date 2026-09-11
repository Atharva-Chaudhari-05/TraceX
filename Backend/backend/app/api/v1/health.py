from fastapi import APIRouter
from sqlalchemy import text

from backend.app.core.neo4j import verify_connection
from backend.app.core.postgres import engine


router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TraceX",
    }


@router.get("/ready")
def readiness():
    postgres_ok = False
    neo4j_ok = False

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        postgres_ok = True
    except Exception:
        pass

    neo4j_ok = verify_connection()

    status = "ready" if postgres_ok and neo4j_ok else "not_ready"

    return {
        "status": status,
        "dependencies": {
            "postgresql": postgres_ok,
            "neo4j": neo4j_ok,
        },
    }