from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from database.db import init_db, SessionLocal, Endpoint
from core.scheduler import start_scheduler, stop_scheduler, add_endpoint_job
from app.routes.endpoints import router as endpoints_router
from app.routes.stats import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    db = SessionLocal()
    try:
        endpoints = db.query(Endpoint).filter(Endpoint.active == True).all()
        for ep in endpoints:
            add_endpoint_job(ep.id, ep.url, ep.interval_mins)
    finally:
        db.close()
    yield
    stop_scheduler()


app = FastAPI(
    title="API Health Monitor",
    description="Automated REST API health monitoring with scheduling and alerts",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(endpoints_router)
app.include_router(stats_router)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "running", "version": "1.0.0"}