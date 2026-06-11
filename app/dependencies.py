
from aiohttp import ClientSession
from fastapi import Request

def get_http_client(request: Request) -> ClientSession:
    return request.app.state.http_client