from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import re

app = FastAPI(title="Student Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # The '*' means allow any computer in the world to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class LoginRequest(BaseModel):
    roll_number: str
    password: str

class FestForm(BaseModel):
    roll_number: str
    name: str
    branch: str
    batch_year: str
    payment_type: str

class ReportForm(BaseModel):
    roll_number: str
    issue_type: str
    description: str

# Helper function to connect to DB
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row  # Returns rows as dictionaries
    return conn

@app.post("/login")
async def login(request: LoginRequest):
    # We treat roll_number as a generic 'user_id' here
    user_id = request.roll_number.strip().lower()
    
    # 1. SECURITY CHECK: Is it an Admin ID OR a valid Student Roll Number?
    is_admin = user_id.startswith("admin_")
    is_student = re.match(r"^\d{2}[a-z0-9]{2}\d[a-z][a-z0-9]{4}$", user_id)
    
    if not (is_admin or is_student):
        raise HTTPException(status_code=400, detail="Invalid format. Must be a 10-character Roll Number or Admin ID.")
        
    # 2. Secure DB Check
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE roll_number = ? AND password = ?", 
        (user_id, request.password)
    ).fetchone()
    conn.close()
    
    if user:
        return {"success": True, "data": dict(user)}
    else:
        raise HTTPException(status_code=401, detail="Invalid ID or Password")

@app.get("/results/{roll_number}")
async def get_results(roll_number: str):
    conn = get_db_connection()
    result = conn.execute("SELECT * FROM results WHERE roll_number = ?", (roll_number,)).fetchone()
    conn.close()
    
    if result:
        return dict(result)
    raise HTTPException(status_code=404, detail="Not Registered")

@app.get("/syllabus/{batch_year}")
async def get_syllabus(batch_year: str):
    conn = get_db_connection()
    syllabus = conn.execute("SELECT * FROM syllabus WHERE batch_year = ?", (batch_year,)).fetchone()
    conn.close()
    
    if syllabus:
        return dict(syllabus)
    raise HTTPException(status_code=404, detail="Syllabus not updated for this batch")

@app.post("/register-fest")
async def register_fest(form: FestForm):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO fest_registrations (roll_number, name, branch, batch_year, payment_type) VALUES (?, ?, ?, ?, ?)",
        (form.roll_number, form.name, form.branch, form.batch_year, form.payment_type)
    )
    conn.commit()
    conn.close()
    return {"success": True, "message": "Fest Registration Successful!"}

@app.post("/submit-report")
async def submit_report(form: ReportForm):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO reports (roll_number, issue_type, description) VALUES (?, ?, ?)",
        (form.roll_number, form.issue_type, form.description)
    )
    conn.commit()
    conn.close()
    return {"success": True, "message": "Report submitted securely to administration."}

class EventRegistration(BaseModel):
    roll_number: str
    event_name: str

@app.post("/register-event")
async def register_event(data: EventRegistration):
    conn = get_db_connection()
    # Check if they already registered to prevent duplicates
    existing = conn.execute(
        "SELECT * FROM event_registrations WHERE roll_number = ? AND event_name = ?", 
        (data.roll_number, data.event_name)
    ).fetchone()
    
    if existing:
        conn.close()
        return {"success": False, "message": "You are already registered for this event!"}
        
    conn.execute(
        "INSERT INTO event_registrations (roll_number, event_name) VALUES (?, ?)",
        (data.roll_number, data.event_name)
    )
    conn.commit()
    conn.close()
    return {"success": True, "message": "Successfully registered!"}

@app.get("/my-events/{roll_number}")
async def get_my_events(roll_number: str):
    conn = get_db_connection()
    events = conn.execute(
        "SELECT event_name FROM event_registrations WHERE roll_number = ?", 
        (roll_number,)
    ).fetchall()
    conn.close()
    
    # Convert database rows into a simple list of event names
    event_list = [row['event_name'] for row in events]
    return {"events": event_list}
# Fetches all past results for a specific student to draw the chart
@app.get("/chart-results/{roll_number}")
async def get_chart_results(roll_number: str):
    conn = get_db_connection()
    results = conn.execute(
        "SELECT semester, gpa FROM results WHERE roll_number = ? ORDER BY semester", 
        (roll_number,)
    ).fetchall()
    conn.close()
    
    return {"data": [dict(row) for row in results]}

# Secure Admin Endpoint: Fetches every report submitted by any student
@app.get("/admin/all-reports")
async def get_all_reports():
    conn = get_db_connection()
    reports = conn.execute("SELECT * FROM reports").fetchall()
    conn.close()
    return {"reports": [dict(row) for row in reports]}