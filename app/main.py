import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import (
    BudgetlyException,
    budgetly_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.database import create_tables
from app.api.v1.routes import health, auth, ai, reports, exports

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await create_tables()
    logger.info("Budgetly API started", version=settings.APP_VERSION)
    yield
    logger.info("Budgetly API shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered personal finance assistant API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.add_exception_handler(BudgetlyException, budgetly_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

prefix = settings.API_V1_PREFIX
app.include_router(health.router, prefix=prefix, tags=["Health"])
app.include_router(auth.router, prefix=prefix, tags=["Authentication"])
app.include_router(ai.router, prefix=prefix, tags=["AI"])
app.include_router(reports.router, prefix=prefix, tags=["Reports"])
app.include_router(exports.router, prefix=prefix, tags=["Export & Backup"])
