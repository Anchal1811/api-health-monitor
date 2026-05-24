from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db, Endpoint, PingLog
from app.schemas import EndpointCreate, EndpointResponse, PingLogResponse, EndpointStats
from core.scheduler import add_endpoint_job, remove_endpoint_job
from core.pinger import check_ssl_expiry

router = APIRouter(prefix="/endpoints", tags=["Endpoints"])


@router.post("/", response_model=EndpointResponse, status_code=201)
def add_endpoint(payload: EndpointCreate, db: Session = Depends(get_db)):
    existing = db.query(Endpoint).filter(Endpoint.url == payload.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL already being monitored")
    endpoint = Endpoint(
        name=payload.name,
        url=payload.url,
        interval_mins=payload.interval_mins,
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    add_endpoint_job(endpoint.id, endpoint.url, endpoint.interval_mins)
    return endpoint


@router.get("/", response_model=List[EndpointResponse])
def list_endpoints(db: Session = Depends(get_db)):
    return db.query(Endpoint).filter(Endpoint.active == True).all()


@router.delete("/{endpoint_id}", status_code=204)
def delete_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    remove_endpoint_job(endpoint_id)
    db.delete(endpoint)
    db.commit()


@router.get("/{endpoint_id}/history", response_model=List[PingLogResponse])
def get_history(endpoint_id: int, limit: int = 50, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    logs = (
        db.query(PingLog)
        .filter(PingLog.endpoint_id == endpoint_id)
        .order_by(PingLog.checked_at.desc())
        .limit(limit)
        .all()
    )
    return logs


@router.get("/{endpoint_id}/stats", response_model=EndpointStats)
def get_stats(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    logs = db.query(PingLog).filter(PingLog.endpoint_id == endpoint_id).all()
    total = len(logs)
    if total == 0:
        return EndpointStats(
            endpoint_id=endpoint_id, name=endpoint.name, url=endpoint.url,
            total_checks=0, uptime_percent=0.0, avg_response_ms=None,
            last_checked=None, current_status="UNKNOWN", ssl_info=None,
        )
    up_count = sum(1 for l in logs if l.is_up)
    uptime_pct = round((up_count / total) * 100, 2)
    response_times = [l.response_ms for l in logs if l.response_ms is not None]
    avg_ms = round(sum(response_times) / len(response_times), 2) if response_times else None
    last_log = sorted(logs, key=lambda l: l.checked_at, reverse=True)[0]
    ssl_info = check_ssl_expiry(endpoint.url)
    return EndpointStats(
        endpoint_id=endpoint_id, name=endpoint.name, url=endpoint.url,
        total_checks=total, uptime_percent=uptime_pct, avg_response_ms=avg_ms,
        last_checked=last_log.checked_at,
        current_status="UP" if last_log.is_up else "DOWN",
        ssl_info=ssl_info,
    )