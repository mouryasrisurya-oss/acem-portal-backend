from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import re

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- SCHEMAS ---
class LoginRequest(BaseModel): roll_number: str; password: str
class ReportIssue(BaseModel): roll_number: str; issue_type: str; description: str
class AttendanceUpdate(BaseModel): roll_number: str; total_classes: int; attended_classes: int
class CurriculumAdd(BaseModel): branch: str; semester: str; subject_code: str; subject_name: str; subject_type: str
class EventCreate(BaseModel): title: str; date: str; description: str; faculty: str; contact: str
class FestRegistration(BaseModel): roll_number: str; name: str; branch: str; batch_year: str; payment_type: str
class EventRegistration(BaseModel): roll_number: str; event_name: str

# NEW: Schemas for Adding Students and Updating Profiles
class StudentCreate(BaseModel): roll_number: str; password: str; name: str; batch_year: str; branch: str
class ProfileUpdate(BaseModel): roll_number: str; name: str; branch: str; phone: str; blood_group: str

# --- AUTH API ---
@app.post("/login")
async def login(request: LoginRequest):
    user_id = request.roll_number.strip().lower()
    if not (user_id.startswith("admin_") or re.match(r"^\d{2}[a-z0-9]{2}\d[a-z][a-z0-9]{4}$", user_id)):
        raise HTTPException(status_code=400, detail="Invalid format.")
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE roll_number = ? AND password = ?", (user_id, request.password)).fetchone()
    conn.close()
    if user: return {"success": True, "data": dict(user)}
    raise HTTPException(status_code=401, detail="Invalid ID or Password")

# --- STUDENT APIs ---
@app.post("/student/update-profile")
async def update_profile(data: ProfileUpdate):
    conn = get_db_connection()
    conn.execute('''
        UPDATE users SET name = ?, branch = ?, phone = ?, blood_group = ? WHERE roll_number = ?
    ''', (data.name, data.branch, data.phone, data.blood_group, data.roll_number))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Profile updated successfully!"}

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
    conn.commit(); conn.close()
    return {"success": True, "message": "Report submitted securely!"}

@app.post("/register-fest")
async def register_fest(data: FestRegistration):
    conn = get_db_connection()
    if conn.execute("SELECT * FROM fest_registrations WHERE roll_number = ?", (data.roll_number,)).fetchone():
        conn.close(); return {"success": False, "message": "Already registered for Fest!"}
    conn.execute("INSERT INTO fest_registrations (roll_number, name, branch, payment_type) VALUES (?, ?, ?, ?)", (data.roll_number, data.name, data.branch, data.payment_type))
    conn.commit(); conn.close()
    return {"success": True, "message": "Registration Confirmed!"}

@app.get("/events")
async def get_events():
    conn = get_db_connection(); events = conn.execute("SELECT * FROM campus_events").fetchall(); conn.close()
    return {"data": [dict(row) for row in events]}

@app.post("/register-event")
async def register_event(data: EventRegistration):
    conn = get_db_connection()
    if conn.execute("SELECT * FROM event_registrations WHERE roll_number = ? AND event_title = ?", (data.roll_number, data.event_name)).fetchone():
        conn.close(); return {"success": False, "message": "Already registered!"}
    conn.execute("INSERT INTO event_registrations (roll_number, event_title) VALUES (?, ?)", (data.roll_number, data.event_name))
    conn.commit(); conn.close()
    return {"success": True, "message": "Successfully registered!"}

@app.get("/my-events/{roll_number}")
async def get_my_events(roll_number: str):
    conn = get_db_connection(); events = conn.execute("SELECT event_title FROM event_registrations WHERE roll_number = ?", (roll_number,)).fetchall(); conn.close()
    return {"events": [row['event_title'] for row in events]}

# --- ADMIN APIs ---
# NEW: Admin Adds Student
@app.post("/admin/add-student")
async def add_student(data: StudentCreate):
    conn = get_db_connection()
    # Check if student already exists
    if conn.execute("SELECT * FROM users WHERE roll_number = ?", (data.roll_number,)).fetchone():
        conn.close()
        return {"success": False, "message": "Student Roll Number already exists!"}
    
    conn.execute('''
        INSERT INTO users (roll_number, password, name, batch_year, branch, role, phone, blood_group) 
        VALUES (?, ?, ?, ?, ?, 'student', 'Not Set', 'Not Set')
    ''', (data.roll_number.lower(), data.password, data.name, data.batch_year, data.branch))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Student {data.name} added successfully!"}

@app.post("/admin/add-curriculum")
async def add_curriculum(data: CurriculumAdd):
    conn = get_db_connection()
    
    # NEW: The Strict 6 Theory / 5 Lab Security Check
    current_count = conn.execute(
        "SELECT COUNT(*) FROM curriculum WHERE branch = ? AND semester = ? AND subject_type = ?", 
        (data.branch, data.semester, data.subject_type)
    ).fetchone()[0]
    
    if data.subject_type == "Theory" and current_count >= 6:
        conn.close()
        return {"success": False, "message": "Limit Reached: Maximum 6 Theory subjects allowed per semester."}
    
    if data.subject_type == "Lab" and current_count >= 5:
        conn.close()
        return {"success": False, "message": "Limit Reached: Maximum 5 Laboratory subjects allowed per semester."}
        
    conn.execute('INSERT INTO curriculum (branch, semester, subject_code, subject_name, subject_type) VALUES (?, ?, ?, ?, ?)', 
                 (data.branch, data.semester, data.subject_code, data.subject_name, data.subject_type))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"{data.subject_type} Subject added successfully!"}

@app.post("/admin/update-attendance")
async def update_attendance(data: AttendanceUpdate):
    percentage = round((data.attended_classes / data.total_classes) * 100, 2)
    conn = get_db_connection(); conn.execute('INSERT OR REPLACE INTO attendance (roll_number, total_classes, attended_classes, percentage) VALUES (?, ?, ?, ?)', (data.roll_number, data.total_classes, data.attended_classes, percentage)); conn.commit(); conn.close()
    return {"success": True, "message": f"Updated! {percentage}%"}

@app.get("/admin/dashboard-stats")
async def get_dashboard_stats():
    conn = get_db_connection(); reports = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'Pending'").fetchone()[0]; events = conn.execute("SELECT COUNT(*) FROM event_registrations").fetchone()[0]; fest = conn.execute("SELECT COUNT(*) FROM fest_registrations").fetchone()[0]; upi = conn.execute("SELECT COUNT(*) FROM fest_registrations WHERE payment_type IN ('PhonePe', 'GooglePay')").fetchone()[0]; conn.close()
    return {"pending_reports": reports, "total_event_regs": events, "fest_total": fest, "fest_upi": upi}

@app.get("/admin/all-reports")
async def get_all_reports():
    conn = get_db_connection(); r = conn.execute("SELECT * FROM reports ORDER BY id DESC").fetchall(); conn.close()
    return {"reports": [dict(row) for row in r]}

@app.get("/admin/fest-registrations")
async def get_fest_registrations():
    conn = get_db_connection(); r = conn.execute("SELECT * FROM fest_registrations ORDER BY id DESC").fetchall(); conn.close()
    return {"data": [dict(row) for row in r]}

@app.post("/admin/add-event")
async def admin_add_event(data: EventCreate):
    conn = get_db_connection(); conn.execute('INSERT INTO campus_events (title, date, description, faculty, contact) VALUES (?, ?, ?, ?, ?)', (data.title, data.date, data.description, data.faculty, data.contact)); conn.commit(); conn.close()
    return {"success": True, "message": "Event published!"}

@app.delete("/admin/delete-event/{event_id}")
async def admin_delete_event(event_id: int):
    conn = get_db_connection(); conn.execute('DELETE FROM campus_events WHERE id = ?', (event_id,)); conn.commit(); conn.close()
    return {"success": True}

@app.get("/admin/event-stats")
async def get_event_stats():
    conn = get_db_connection()
    stats = conn.execute('SELECT e.title, e.faculty, COUNT(r.id) as student_count FROM campus_events e LEFT JOIN event_registrations r ON e.title = r.event_title GROUP BY e.title').fetchall()
    details = conn.execute('SELECT r.event_title, u.roll_number, u.name FROM event_registrations r JOIN users u ON r.roll_number = u.roll_number').fetchall()
    conn.close()
    return {"stats": [dict(row) for row in stats], "details": [dict(row) for row in details]}