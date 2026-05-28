from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- SCHEMAS ---
class LoginRequest(BaseModel):
    roll_number: str
    password: str

class EventRegistration(BaseModel):
    roll_number: str
    event_name: str

class ReportIssue(BaseModel):
    roll_number: str
    issue_type: str
    description: str

class AttendanceUpdate(BaseModel):
    roll_number: str
    total_classes: int
    attended_classes: int

class CurriculumAdd(BaseModel):
    branch: str
    semester: str
    subject_code: str
    subject_name: str

class EventCreate(BaseModel):
    title: str
    date: str
    description: str
    faculty: str
    contact: str

class FestRegistration(BaseModel):
    roll_number: str
    name: str
    branch: str
    batch_year: str
    payment_type: str

# --- AUTH API ---
@app.post("/login")
async def login(request: LoginRequest):
    user_id = request.roll_number.strip().lower()
    is_admin = user_id.startswith("admin_")
    is_student = re.match(r"^\d{2}[a-z0-9]{2}\d[a-z][a-z0-9]{4}$", user_id)
    
    if not (is_admin or is_student):
        raise HTTPException(status_code=400, detail="Invalid format.")
        
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE roll_number = ? AND password = ?", (user_id, request.password)).fetchone()
    conn.close()
    if user: return {"success": True, "data": dict(user)}
    raise HTTPException(status_code=401, detail="Invalid ID or Password")

# --- STUDENT APIs ---
@app.get("/attendance/{roll_number}")
async def get_attendance(roll_number: str):
    conn = get_db_connection()
    record = conn.execute("SELECT * FROM attendance WHERE roll_number = ?", (roll_number,)).fetchone()
    conn.close()
    if record: return {"success": True, "data": dict(record)}
    return {"success": False}

@app.get("/curriculum/{branch}/{semester}")
async def get_curriculum(branch: str, semester: str):
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM curriculum WHERE branch = ? AND semester = ?", (branch, semester)).fetchall()
    conn.close()
    return {"success": True, "data": [dict(r) for r in records]}

@app.get("/chart-results/{roll_number}")
async def get_chart_results(roll_number: str):
    conn = get_db_connection()
    results = conn.execute("SELECT semester, gpa FROM results WHERE roll_number = ? ORDER BY semester", (roll_number,)).fetchall()
    conn.close()
    return {"data": [dict(row) for row in results]}

@app.post("/submit-report")
async def submit_report(data: ReportIssue):
    conn = get_db_connection()
    conn.execute("INSERT INTO reports (roll_number, issue_type, description) VALUES (?, ?, ?)", (data.roll_number, data.issue_type, data.description))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Report submitted securely!"}

@app.post("/register-fest")
async def register_fest(data: FestRegistration):
    return {"success": True, "message": "Registration Confirmed!"}

# --- DYNAMIC EVENTS APIs (STUDENT & ADMIN) ---
@app.get("/events")
async def get_events():
    conn = get_db_connection()
    events = conn.execute("SELECT * FROM campus_events").fetchall()
    conn.close()
    return {"data": [dict(row) for row in events]}

@app.post("/register-event")
async def register_event(data: EventRegistration):
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM event_registrations WHERE roll_number = ? AND event_title = ?", (data.roll_number, data.event_name)).fetchone()
    if existing:
        conn.close()
        return {"success": False, "message": "Already registered!"}
    conn.execute("INSERT INTO event_registrations (roll_number, event_title) VALUES (?, ?)", (data.roll_number, data.event_name))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Successfully registered!"}

@app.get("/my-events/{roll_number}")
async def get_my_events(roll_number: str):
    conn = get_db_connection()
    events = conn.execute("SELECT event_title FROM event_registrations WHERE roll_number = ?", (roll_number,)).fetchall()
    conn.close()
    return {"events": [row['event_title'] for row in events]}

# --- ADMIN APIs ---
@app.get("/admin/all-reports")
async def get_all_reports():
    conn = get_db_connection()
    reports = conn.execute("SELECT * FROM reports").fetchall()
    conn.close()
    return {"reports": [dict(row) for row in reports]}

@app.post("/admin/update-attendance")
async def update_attendance(data: AttendanceUpdate):
    percentage = round((data.attended_classes / data.total_classes) * 100, 2)
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO attendance (roll_number, total_classes, attended_classes, percentage) VALUES (?, ?, ?, ?)', 
                 (data.roll_number, data.total_classes, data.attended_classes, percentage))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Updated! {percentage}%"}

@app.post("/admin/add-curriculum")
async def add_curriculum(data: CurriculumAdd):
    conn = get_db_connection()
    conn.execute('INSERT INTO curriculum (branch, semester, subject_code, subject_name) VALUES (?, ?, ?, ?)', 
                 (data.branch, data.semester, data.subject_code, data.subject_name))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Subject added!"}

@app.post("/admin/add-event")
async def admin_add_event(data: EventCreate):
    conn = get_db_connection()
    conn.execute('INSERT INTO campus_events (title, date, description, faculty, contact) VALUES (?, ?, ?, ?, ?)', 
                 (data.title, data.date, data.description, data.faculty, data.contact))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Event published!"}

@app.delete("/admin/delete-event/{event_id}")
async def admin_delete_event(event_id: int):
    conn = get_db_connection()
    # Delete the event
    conn.execute('DELETE FROM campus_events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/admin/event-stats")
async def get_event_stats():
    conn = get_db_connection()
    # Gets the count of students per event
    stats = conn.execute('''
        SELECT e.title, e.faculty, COUNT(r.id) as student_count 
        FROM campus_events e 
        LEFT JOIN event_registrations r ON e.title = r.event_title 
        GROUP BY e.title
    ''').fetchall()
    
    # Gets the actual list of names and rolls for each event
    details = conn.execute('''
        SELECT r.event_title, u.roll_number, u.name 
        FROM event_registrations r
        JOIN users u ON r.roll_number = u.roll_number
    ''').fetchall()
    conn.close()
    
    return {"stats": [dict(row) for row in stats], "details": [dict(row) for row in details]}