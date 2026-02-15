# Promise

## Features
- Create promises with a deadline
- View active promises and mark them complete
- Reframe missed promises with AI-generated reframing solutions

## Requirements
- Python 3.9+
- A Gemini API key

## Steps to beginning our project
1) Create a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies - using requirements.txt
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

## Notes - 
- Deadlines use `1h 30m 10s` format.
- The SQLite database is stored in `promises.db`.

---

# Future Additions and Future of our Project!

## 2-way Promises (others)
We want to create a way for 2 people to create promises with each other. The premise is allowing someone, say User1 wants to make a promise to User2. We'll send the promise request to User2. Both creator and participant must accept completion. Then once the promise has been accepted it'll be placed into both parties DBs. When either the timer and/or the creator checks off the promise as complete; either a new request will be sent out to the partipicant and/or the partipicant will update periodically to check if the promise has been completed. 

## World Promises (world)
When we want to create a world promise type; we're identifying a promise that'll take a signficicant amount of time. That's it's main difference bewteen self and world. When someone completes a world promise, that promise, will be shown in the promise feed, and a new promise, even more ambitious, will take it's place.


**Validation**:
- Must have at least one participant for "others" type
- Deadline must be in the future -> Minimum promise length:
- Self promises must be; 1 hr/min
- Other promises must be: 1 hr/min
- World promises must be: 1 day/min

#### Reframing - How reframing works on the backend
```
Step 1: WHY Analysis
├─ System asks: "Why did you miss this promise?"
├─ User provides detailed explanation

Step 2: Categorization
├─ Systems asks user to categorizes into failure type:
│   ├─ TIME_CONSTRAINT: "Not enough time"
│   ├─ RESOURCE_LIMITATION: "Lacked money/tools/support"
│   ├─ EXTERNAL_FACTORS: "Unexpected events"
│   ├─ MOTIVATION_LOSS: "Lost interest/drive"
│   ├─ UNCLEAR_GOALS: "Goal was too vague"
│   ├─ OVERCOMMITMENT: "Took on too much"
│   └─ SKILL_GAP: "Lacked necessary skills"
└─ LLM processes response

Step 3: Solution Generation
├─ System uses category-specific prompts
├─ LLM generates 3 distinct solutions:
│   ├─ Solution 1: Conservative (smaller scope)
│   ├─ Solution 2: Moderate (adjusted timeline/resources)
│   └─ Solution 3: Creative (alternative approach)
└─ Each solution includes:
    ├─ Revised promise text
    ├─ New deadline
    ├─ Why this approach works

Step 4: Selection & Update
├─ User reviews all 3 solutions
├─ Selects one 
└─ Promise update (overrides originla promise, old is updated but not completely replaced)
