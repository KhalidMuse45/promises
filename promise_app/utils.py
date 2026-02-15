import hashlib
import re
import time


def now_seconds():
    return int(time.time())


def parse_duration(value):
    text = ""
    if value:
        text = value
    text = text.strip().lower()
    if text == "":
        return None

    total = 0
    matches = re.findall(r"(\d+)\s*(h|m|s)", text)
    if not matches:
        return None

    for amount, unit in matches:
        amount = int(amount)
        if unit == "h":
            total += amount * 3600
        elif unit == "m":
            total += amount * 60
        else:
            total += amount

    if total > 0:
        return total
    return None


def format_duration(total_seconds):
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def parse_update(text):
    name = ""
    promise = ""
    deadline = ""
    lines_text = ""
    if text:
        lines_text = text
    for line in lines_text.splitlines():
        line = line.strip()
        if line.lower().startswith("name:"):
            name = line.split(":", 1)[1].strip()
        elif line.lower().startswith("promise:"):
            promise = line.split(":", 1)[1].strip()
        elif line.lower().startswith("deadline:"):
            deadline = line.split(":", 1)[1].strip()
    return name, promise, deadline


def parse_create(text):
    name = ""
    promise_type = ""
    promise = ""
    lines_text = ""
    if text:
        lines_text = text
    for line in lines_text.splitlines():
        line = line.strip()
        if line.lower().startswith("name:"):
            name = line.split(":", 1)[1].strip()
        elif line.lower().startswith("type:"):
            promise_type = line.split(":", 1)[1].strip().lower()
        elif line.lower().startswith("promise:"):
            promise = line.split(":", 1)[1].strip()
    return name, promise_type, promise


def hash_promise(promise_id, created_at, name, promise_type, content):
    base = f"{promise_id}|{created_at}|{name}|{promise_type}|{content}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
