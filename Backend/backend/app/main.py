from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.ingestion import router as ingestion_router
from backend.app.api.v1.extraction import router as extraction_router
from backend.app.api.v1.resolution import router as resolution_router
from backend.app.api.v1.graph import router as graph_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.audit import router as audit_router
from backend.app.api.v1.cases import router as cases_router
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging
from backend.app.core.postgres import engine
from backend.app.auth.models import User, Role
from backend.app.auth.security import get_password_hash


def _bootstrap_dev_user():
    """Safely bootstrap a development user if configured and none exists."""
    if settings.app_env != "development":
        return
        
    email = settings.bootstrap_admin_email
    password = settings.bootstrap_admin_password
    
    if not email or not password:
        return
        
    try:
        with Session(engine) as session:
            user = session.scalar(select(User).where(User.email == email))
            if not user:
                # Create bootstrap user
                new_user = User(
                    email=email,
                    hashed_password=get_password_hash(password),
                    is_active=True,
                )
                
                # Fetch Admin role
                admin_role = session.scalar(select(Role).where(Role.name == "Admin"))
                if admin_role:
                    new_user.roles.append(admin_role)
                    
                session.add(new_user)
                session.commit()
            else:
                # Ensure the user has the Admin role if they were already created
                admin_role = session.scalar(select(Role).where(Role.name == "Admin"))
                if admin_role and admin_role not in user.roles:
                    user.roles.append(admin_role)
                    session.commit()
    except Exception as exc:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    _bootstrap_dev_user()
    yield


from backend.app.core.errors import setup_exception_handlers
from backend.app.core.middleware import RequestCorrelationMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestCorrelationMiddleware)
setup_exception_handlers(app)

app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"],
)

app.include_router(
    ingestion_router,
    prefix="/api/v1/ingestion",
    tags=["Ingestion"],
)

app.include_router(
    extraction_router,
    prefix="/api/v1",
)

app.include_router(
    resolution_router,
    prefix="/api/v1",
)

app.include_router(
    graph_router,
    prefix="/api/v1/graph",
    tags=["Graph"],
)

app.include_router(
    analytics_router,
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)

app.include_router(
    audit_router,
    prefix="/api/v1/audit",
    tags=["Audit"],
)

app.include_router(
    cases_router,
    prefix="/api/v1/cases",
    tags=["Cases"],
)

from backend.app.api.v1.ml import router as ml_router

app.include_router(
    ml_router,
    prefix="/api/v1/ml",
    tags=["ML"],
)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }