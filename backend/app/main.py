import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger, request_id_var
from app.api.routes_inference import router as inference_router
from app.api.routes_rag import router as rag_router
from app.api.routes_batch import router as batch_router
from app.api.routes_evaluation import router as evaluation_router
from app.api.routes_monitoring import router as monitoring_router
from app.api.routes_tutorial import router as tutorial_router
from app.storage.database import init_db
from app.storage.seed_data import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    init_db()
    seed_all()
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def inject_request_id(request: Request, call_next):
    rid = uuid.uuid4().hex[:12]
    request_id_var.set(rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


app.include_router(inference_router)
app.include_router(rag_router)
app.include_router(batch_router)
app.include_router(evaluation_router)
app.include_router(monitoring_router)
app.include_router(tutorial_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}
