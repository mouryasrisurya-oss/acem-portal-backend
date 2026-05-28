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
# --- NEW: ATTENDANCE & CURRICULUM SCHEMAS ---
class AttendanceUpdate(BaseModel):
    roll_number: str
    total_classes: int
    attended_classes: int

class CurriculumAdd(BaseModel):
    branch: str
    semester: str
    subject_code: str
    subject_name: str

# --- NEW: STUDENT ENDPOINTS ---
@app.get("/attendance/{roll_number}")
async def get_attendance(roll_number: str):
    conn = get_db_connection()
    record = conn.execute("SELECT * FROM attendance WHERE roll_number = ?", (roll_number,)).fetchone()
    conn.close()
    if record:
        return {"success": True, "data": dict(record)}
    return {"success": False, "message": "No attendance data found."}

@app.get("/curriculum/{branch}/{semester}")
async def get_curriculum(branch: str, semester: str):
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM curriculum WHERE branch = ? AND semester = ?", (branch, semester)).fetchall()
    conn.close()
    return {"success": True, "data": [dict(r) for r in records]}

# --- NEW: ADMIN ENDPOINTS ---
@app.post("/admin/update-attendance")
async def update_attendance(data: AttendanceUpdate):
    percentage = round((data.attended_classes / data.total_classes) * 100, 2)
    conn = get_db_connection()
    # Insert or Replace updates the row if the student already exists
    conn.execute('''
        INSERT OR REPLACE INTO attendance (roll_number, total_classes, attended_classes, percentage)
        VALUES (?, ?, ?, ?)
    ''', (data.roll_number, data.total_classes, data.attended_classes, percentage))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Attendance updated! New percentage: {percentage}%"}

@app.post("/admin/add-curriculum")
async def add_curriculum(data: CurriculumAdd):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO curriculum (branch, semester, subject_code, subject_name)
        VALUES (?, ?, ?, ?)
    ''', (data.branch, data.semester, data.subject_code, data.subject_name))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Subject added to curriculum successfully!"}