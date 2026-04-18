import json
from pathlib import Path

from fastapi.responses import FileResponse

from core import app, WIDGETS, warm_cache
from widgets_uk_housing import router as uk_router
from widgets_nyc_taxi import router as nyc_router

app.include_router(uk_router)
app.include_router(nyc_router)


@app.on_event("startup")
def startup():
    warm_cache()

THUMBNAILS_DIR = Path(__file__).parent / "thumbnails"


@app.get("/")
def root():
    return {"status": "ok", "app": "ClickHouse Explorer", "version": "1.0.0"}


@app.get("/widgets.json")
def get_widgets():
    return WIDGETS


@app.get("/apps.json")
def get_apps():
    return json.load((Path(__file__).parent / "apps.json").open())


@app.get("/thumbnails/{name}")
def get_thumbnail(name: str):
    return FileResponse(THUMBNAILS_DIR / f"{name}.svg", media_type="image/svg+xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7781)
