# Promise

Promise Tracker is a lightweight FastAPI app for creating, tracking, and reframing promises.

## Features
- Create promises with a deadline
- View active promises and mark them complete
- Reframe missed promises with AI-generated solutions

## Requirements
- Python 3.9+
- A Gemini API key (for reframing)

## Setup
1) Create a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```
python3 -m pip install -r requirements.txt
```

3) Add your API key
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
```

## Run
```
python3 -m uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## Notes
- Deadlines use `1h 30m 10s` format.
- The SQLite database is stored in `promises.db`.
