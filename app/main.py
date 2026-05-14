import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controller.draw_controller import router as draw_router
from app.controller.health_controller import router as health_router
from app.controller.participant_controller import router as participant_router
from app.controller.question_controller import router as question_router
from app.controller.super_fa_question_controller import router as super_fa_question_router
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await asyncio.to_thread(init_db)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(participant_router)
app.include_router(question_router)
app.include_router(super_fa_question_router)
app.include_router(draw_router)


@app.get("/")
def root():
    return {"service": settings.app_name, "docs": "/docs"}
