from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from gemini_client import refine_promise
from gemini_client import generate_updated_promise
from gemini_client import format_new_promise

from .db import get_db
from .models import Promise
from .services import get_dashboard_state
from .utils import hash_promise
from .utils import now_seconds
from .utils import parse_create
from .utils import parse_duration
from .utils import parse_update


router = APIRouter()
templates = Jinja2Templates(directory="templates")

PROMISE_TYPES = {
    "self": "self",
    "others": "others",
    "other": "others",
    "world": "world",
}


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db=Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        }
    )


@router.get("/dashboard")
def dashboard():
    return RedirectResponse("/promises", status_code=302)


@router.get("/make", response_class=HTMLResponse)
def make_page(request: Request, db=Depends(get_db)):
    display_promises, missed_promise = get_dashboard_state(db)
    if missed_promise:
        return RedirectResponse("/reframe", status_code=302)
    return templates.TemplateResponse(
        "make.html",
        {
            "request": request,
            "error": "",
        }
    )


@router.get("/promises", response_class=HTMLResponse)
def view_promises(request: Request, db=Depends(get_db)):
    display_promises, missed_promise = get_dashboard_state(db)
    if missed_promise:
        return RedirectResponse("/reframe", status_code=302)
    return templates.TemplateResponse(
        "view.html",
        {
            "request": request,
            "promises": display_promises,
        }
    )


@router.get("/reframe", response_class=HTMLResponse)
def reframe_page(request: Request, db=Depends(get_db)):
    display_promises, missed_promise = get_dashboard_state(db)
    if not missed_promise:
        return RedirectResponse("/promises", status_code=302)
    return templates.TemplateResponse(
        "reframe.html",
        {
            "request": request,
            "promise": missed_promise,
            "solutions": "",
            "reason": "",
            "category": "",
            "error": "",
        }
    )


@router.post("/promises")
def create_promise(
    request: Request,
    raw_text: str = Form(...),
    details: str = Form(None),
    deadline: str = Form(...),
    db=Depends(get_db),
):
    if details:
        raw_text = raw_text + " (" + details + ")"
    formatted = format_new_promise(raw_text)
    parsed = parse_create(formatted)
    name = parsed[0]
    promise_type = parsed[1]
    content = parsed[2]
    if promise_type not in PROMISE_TYPES.values():
        promise_type = "self"

    if not name or not promise_type or not content:
        raise HTTPException(status_code=400, detail="Failed to format promise")

    deadline_seconds = parse_duration(deadline)
    if not deadline_seconds:
        raise HTTPException(status_code=400, detail="Invalid deadline format")

    created_at = now_seconds()
    deadline_at = created_at + deadline_seconds
    hash_value = hash_promise(0, created_at, name, promise_type, content)

    promise = Promise(
        name=name,
        promise_type=promise_type,
        content=content,
        created_at=created_at,
        deadline_at=deadline_at,
        status="ACTIVE",
        hash_value=hash_value,
    )
    db.add(promise)
    db.commit()

    promise.hash_value = hash_promise(promise.id, created_at, name, promise_type, content)
    db.commit()
    return RedirectResponse("/promises", status_code=302)


@router.post("/promises/{promise_id}/complete")
def complete_promise(request: Request, promise_id: int, db=Depends(get_db)):
    promise = db.query(Promise).filter(Promise.id == promise_id).first()
    if promise:
        promise.status = "COMPLETED"
        db.commit()
    return RedirectResponse("/promises", status_code=302)


@router.post("/reframe/{promise_id}/solutions", response_class=HTMLResponse)
def generate_solutions(
    request: Request,
    promise_id: int,
    reason: str = Form(...),
    category: str = Form(...),
    db=Depends(get_db),
):
    promise = db.query(Promise).filter(Promise.id == promise_id).first()
    if not promise:
        raise HTTPException(status_code=404, detail="Promise not found")

    solutions = refine_promise(promise.content, reason, category)
    display_promises, missed_promise = get_dashboard_state(db)
    if not missed_promise or missed_promise.id != promise.id:
        missed_promise = promise

    return templates.TemplateResponse(
        "reframe.html",
        {
            "request": request,
            "promise": missed_promise,
            "solutions": solutions,
            "reason": reason,
            "category": category,
            "error": "",
        }
    )


@router.post("/reframe/{promise_id}/apply")
def apply_reframe(
    request: Request,
    promise_id: int,
    solution: str = Form(...),
    reason: str = Form(...),
    category: str = Form(...),
    db=Depends(get_db),
):
    promise = db.query(Promise).filter(Promise.id == promise_id).first()
    if not promise:
        raise HTTPException(status_code=404, detail="Promise not found")

    solution_label = "Conservative"
    if solution == "2":
        solution_label = "Moderate"
    if solution == "3":
        solution_label = "Progressive"

    update_text = generate_updated_promise(promise.content, reason, category, solution_label)
    parsed = parse_update(update_text)
    name = parsed[0]
    new_content = parsed[1]
    new_deadline = parsed[2]

    deadline_seconds = parse_duration(new_deadline)
    if not name or not new_content or not deadline_seconds:
        raise HTTPException(status_code=400, detail="Failed to parse update")

    created_at = now_seconds()
    deadline_at = created_at + deadline_seconds
    hash_value = hash_promise(0, created_at, name, promise.promise_type, new_content)

    new_promise = Promise(
        name=name,
        promise_type=promise.promise_type,
        content=new_content,
        created_at=created_at,
        deadline_at=deadline_at,
        status="ACTIVE",
        hash_value=hash_value,
    )
    db.add(new_promise)
    db.delete(promise)
    db.commit()

    new_promise.hash_value = hash_promise(new_promise.id, created_at, name, promise.promise_type, new_content)
    db.commit()
    return RedirectResponse("/promises", status_code=302)
