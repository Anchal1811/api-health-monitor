from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database.db import SessionLocal, PingLog
from core.pinger import ping_endpoint
from datetime import datetime

scheduler = BackgroundScheduler()
_last_status = {}


def run_ping_job(endpoint_id: int, url: str):
    db = SessionLocal()
    try:
        result = ping_endpoint(url)
        log = PingLog(
            endpoint_id=endpoint_id,
            status_code=result["status_code"],
            response_ms=result["response_ms"],
            is_up=result["is_up"],
            error_msg=result["error_msg"],
            checked_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
        prev = _last_status.get(endpoint_id, True)
        if prev and not result["is_up"]:
            print(f"[ALERT] {url} is DOWN — {result['error_msg'] or result['status_code']}")
        _last_status[endpoint_id] = result["is_up"]
    finally:
        db.close()


def add_endpoint_job(endpoint_id: int, url: str, interval_mins: int):
    job_id = f"endpoint_{endpoint_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    scheduler.add_job(
        run_ping_job,
        trigger=IntervalTrigger(minutes=interval_mins),
        id=job_id,
        args=[endpoint_id, url],
        replace_existing=True,
        max_instances=1,
    )
    run_ping_job(endpoint_id, url)


def remove_endpoint_job(endpoint_id: int):
    job_id = f"endpoint_{endpoint_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)


def start_scheduler():
    if not scheduler.running:
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)