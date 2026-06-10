
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.news import router as news_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="News Service",
    lifespan=lifespan
)

app.include_router(health_router)
app.include_router(news_router)