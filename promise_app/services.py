from .models import Promise
from .utils import format_duration
from .utils import now_seconds


def get_dashboard_state(db):
    now = now_seconds()
    active_promises = db.query(Promise).filter(Promise.status == "ACTIVE").all()
    for promise in active_promises:
        if promise.deadline_at <= now:
            promise.status = "MISSED"
    db.commit()

    missed_promise = db.query(Promise).filter(Promise.status == "MISSED").order_by(Promise.deadline_at.asc()).first()
    display_promises = db.query(Promise).filter(Promise.status == "ACTIVE").order_by(Promise.deadline_at.asc()).all()
    for promise in display_promises:
        time_left = promise.deadline_at - now
        if time_left < 0:
            time_left = 0
        promise.time_left = format_duration(time_left)
    return display_promises, missed_promise
