from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random, re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

questions_db = {
    "software_engineer_frontend_technical_beginner": [
        {"question": "What does HTML stand for?", "answer": "hypertext markup language"},
        {"question": "Explain the box model in CSS.", "answer": "content padding border margin"},
        {"question": "How do you declare a variable in JavaScript?", "answer": "var let const"},
        {"question": "What is event bubbling?", "answer": "event propagates children parents"},
        {"question": "What is the DOM?", "answer": "document object model tree structure"},
        {"question": "Difference between == and === in JS?", "answer": "== loose === strict equality type coercion"},
        {"question": "How can you include CSS in HTML?", "answer": "inline internal external stylesheet"},
        {"question": "What are semantic HTML elements?", "answer": "header nav section article aside footer"},
        {"question": "What are media queries? Why use them?", "answer": "responsive design breakpoints screen size"},
        {"question": "What is the use of the alt attribute in images?", "answer": "alternative text accessibility"},
    ],
    "software_engineer_frontend_behavioral_beginner": [
        {"question": "Describe a time you resolved a UI bug under pressure.", "answer": "debugging communication teamwork"},
        {"question": "How would you explain CSS specificity to a teammate?", "answer": "clarity teaching example explanation"},
        # ...8 more 
    ],
    "software_engineer_backend_technical_beginner": [
        {"question": "What is a REST API?", "answer": "representational state transfer endpoint http"},
        {"question": "What is an SQL Injection and how to prevent it?", "answer": "malicious input parameterized prepared statement"},
        {"question": "Explain status code 404.", "answer": "not found resource invalid url"},
        {"question": "Difference between GET and POST requests.", "answer": "get retrieve post submit data body"},
        {"question": "What is a primary key in a database?", "answer": "unique identifier table row"},
        {"question": "How do you run code asynchronously in Python?", "answer": "async await threading multiprocessing"},
        {"question": "Explain the use of indexes in SQL.", "answer": "speed query optimize data retrieval"},
        {"question": "What is an ORM?", "answer": "object relational mapping data database"},
        {"question": "What is server-side rendering?", "answer": "render html server improve seo"},
        {"question": "Difference between SQL and NoSQL databases.", "answer": "structured tables schema flexible documents keys"},
    ],
    "software_engineer_backend_behavioral_beginner": [
        {"question": "Describe a time you migrated a database.", "answer": "planning execution rollback impact"},
        {"question": "How did you handle a major backend outage?", "answer": "root cause recovery communication team"},
        # ...8 more
    ],
    "software_engineer_machine_learning_technical_beginner": [
        {"question": "What is supervised learning?", "answer": "labeled data prediction classification regression"},
        {"question": "What is overfitting?", "answer": "model noise poor generalization validation"},
        {"question": "What is bias-variance tradeoff?", "answer": "underfitting overfitting error generalization"},
        {"question": "Explain what 'features' are in ML.", "answer": "input variables measurable property"},
        {"question": "What is a confusion matrix?", "answer": "performance evaluation prediction actual results"},
        {"question": "Explain cross-validation.", "answer": "partition split data train test"},
        {"question": "Define precision and recall.", "answer": "true positive relevant returned"},
        {"question": "What is the use of regularization?", "answer": "reduce overfitting penalty term complexity"},
        {"question": "What is gradient descent?", "answer": "optimization minimize cost function"},
        {"question": "What is a neural network?", "answer": "model layers neurons features"},
    ],
    "software_engineer_machine_learning_behavioral_beginner": [
        {"question": "Describe a time you explained a model to stakeholders.", "answer": "simple analogy visualization presentation"},
        {"question": "How did you select the right metric for your ML task?", "answer": "goal analysis business requirements"},
        # ...8 more
    ],
    "product_manager_frontend_technical_beginner": [
        {"question": "Give an example of a successful UI improvement you led.", "answer": "impact user satisfaction collaboration"},
        {"question": "How do you ensure design consistency across frontend features?", "answer": "guidelines review cross-team collaboration"},
        # ...8 more 
    ],
    "product_manager_frontend_behavioral_beginner": [
        {"question": "Tell about a challenging discussion with an engineer.", "answer": "communication empathy compromise outcome"},
        {"question": "How do you prioritize which user feedback to address?", "answer": "impact user base feasibility alignment"},
        # ...8 more
    ],
    "product_manager_backend_technical_beginner": [
        {"question": "How do you gather requirements for backend systems?", "answer": "stakeholder interviews documentation use cases"},
        {"question": "Example of a time API changes broke a feature.", "answer": "postmortem fix communication"},
        # ...8 more 
    ],
    "product_manager_backend_behavioral_beginner": [
        {"question": "Describe handling a backend incident as a PM.", "answer": "leadership communication crisis"},
        {"question": "How do you balance new backend features vs. technical debt?", "answer": "prioritization stakeholder input business value"},
        # ...8 more
    ],
    "product_manager_machine_learning_technical_beginner": [
        {"question": "How do you define success for an ML feature?", "answer": "business impact adoption improvement"},
        {"question": "Describe a product launch where ML was a key differentiator.", "answer": "data prediction automation outcome"},
        # ...8 more
    ],
    "product_manager_machine_learning_behavioral_beginner": [
        {"question": "Describe a time you worked with data scientists to improve a product.", "answer": "collaboration metric ai model"},
        {"question": "How do you simplify ML concepts for executives?", "answer": "storytelling analogy business terms"},
        # ...8 more
    ],
    # Add sets for intermediate/advanced by duplicating keys with those suffixes and writing new/complex questions.
}

sessions = {}

# ------------------- NEW: user history -------------------
user_history = {}  # {user_id: [session_ids]}

class StartRequest(BaseModel):
    role: str
    domain: str
    mode: str
    difficulty: str
    user_id: str = None  # optional

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

def keyword_match(user_answer, correct_answer):
    user_answer = user_answer.lower()
    keywords = set(re.findall(r'\w+', correct_answer.lower()))
    if not keywords:
        return 0.0
    matches = sum(1 for kw in keywords if kw in user_answer)
    return matches / len(keywords)

@app.post("/start_interview")
def start_interview(req: StartRequest):
    key = f"{req.role.replace(' ', '_').lower()}_{req.domain.replace(' ', '_').lower()}_{req.mode.lower()}_{req.difficulty.lower()}"
    questions = questions_db.get(key)
    if not questions:
        raise HTTPException(status_code=404, detail=f"No questions configured for your selection ({key})")
    selected_qs = random.sample(questions, k=min(10, len(questions)))
    session_id = str(random.randint(100000, 999999))
    sessions[session_id] = {
        "questions": selected_qs,
        "current": 0,
        "score": 0,
        "answers": [],
        "user_id": req.user_id
    }
    if req.user_id:
        user_history.setdefault(req.user_id, []).append(session_id)
    return {"session_id": session_id}

@app.get("/get_question/{session_id}")
def get_question(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["current"] >= len(session["questions"]):
        return {"done": True}
    question = session["questions"][session["current"]]["question"]
    return {"question": question, "done": False}

@app.post("/submit_answer")
def submit_answer(req: AnswerRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["current"] >= len(session["questions"]):
        return {"done": True, "score": session["score"]}
    correct_answer = session["questions"][session["current"]]["answer"]
    user_answer = req.answer
    accuracy = keyword_match(user_answer, correct_answer)
    correct = accuracy >= 0.5
    if correct:
        session["score"] += 1
    session["answers"].append({
        "question": session["questions"][session["current"]]["question"],
        "correct_answer": correct_answer,
        "user_answer": user_answer,
        "correct": correct,
        "accuracy": round(accuracy * 100, 2),
    })
    session["current"] += 1
    done = session["current"] >= len(session["questions"])
    return {"correct": correct, "done": done, "score": session["score"]}

@app.get("/feedback/{session_id}")
def get_feedback(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "score": session["score"],
        "total": len(session["questions"]),
        "answers": session["answers"],
        "summary": f"You scored {session['score']} out of {len(session['questions'])}."
    }

# ------------------- NEW: user feedback history -------------------
@app.get("/feedback_history/{user_id}")
def feedback_history(user_id: str):
    session_ids = user_history.get(user_id)
    if not session_ids:
        raise HTTPException(status_code=404, detail="No feedback history for this user")
    history = []
    for sid in session_ids:
        sess = sessions.get(sid)
        if sess:
            history.append({
                "session_id": sid,
                "score": sess["score"],
                "total": len(sess["questions"]),
                "answers": sess["answers"]
            })
    return {"user_id": user_id, "history": history}
