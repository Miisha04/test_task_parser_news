
from contextlib import asynccontextmanager

from fastapi import FastAPI
from aiohttp import ClientSession

from app.routers.health import router as health_router
from app.routers.news import router as news_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    client = ClientSession()
    app.state.http_client = client
    
    try:
        yield
    finally:
        await app.state.http_client.close()



app = FastAPI(
    title="News Service",
    lifespan=lifespan
)

app.include_router(health_router)
app.include_router(news_router)