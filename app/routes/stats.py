from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db, Endpoint, PingLog

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/")
def overall_stats(db: Session = Depends(get_db)):
    endpoints = db.query(Endpoint).filter(Endpoint.active == True).all()
    total_endpoints = len(endpoints)
    up_count = 0
    down_count = 0
    for ep in endpoints:
        last_log = (
            db.query(PingLog)
            .filter(PingLog.endpoint_id == ep.id)
            .order_by(PingLog.checked_at.desc())
            .first()
        )
        if last_log:
            if last_log.is_up:
                up_count += 1
            else:
                down_count += 1
    total_pings = db.query(PingLog).count()
    return {
        "total_endpoints": total_endpoints,
        "endpoints_up": up_count,
        "endpoints_down": down_count,
        "total_pings_recorded": total_pings,
    }