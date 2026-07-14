"""FastAPI entrypoint."""

from fastapi import FastAPI

from core import __version__
from core.api.health import router as health_router

app = FastAPI(title="SellerCompass", version=__version__)
app.include_router(health_router)


@app.get("/")
def root() -> dict:
    return {"name": "SellerCompass", "version": __version__, "docs": "/docs"}
