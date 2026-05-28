import sqlite3

def setup_database():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # 1. Reset Tables for the Presentation
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS results')
    cursor.execute('DROP TABLE IF EXISTS attendance')
    cursor.execute('DROP TABLE IF EXISTS curriculum')
    
    # 2. Core Tables
    cursor.execute('CREATE TABLE users (roll_number TEXT PRIMARY KEY, password TEXT, name TEXT, batch_year TEXT, branch TEXT, role TEXT)')
    cursor.execute('CREATE TABLE results (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, semester TEXT, gpa REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, issue_type TEXT, description TEXT, status TEXT DEFAULT "Pending")')
    cursor.execute('CREATE TABLE IF NOT EXISTS event_registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, event_name TEXT)')
    
    # 3. NEW: Attendance & Curriculum Tables
    cursor.execute('''
        CREATE TABLE attendance (
            roll_number TEXT PRIMARY KEY,
            total_classes INTEGER,
            attended_classes INTEGER,
            percentage REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch TEXT,
            semester TEXT,
            subject_code TEXT,
            subject_name TEXT
        )
    ''')

    # --- MOCK DATA ---
    users_data = [
        ('admin_jahnavi', 'admin123', 'Prof. Jahnavi', 'N/A', 'CSE Dept', 'admin'),
        ('admin_tejaswini', 'admin123', 'Prof. Tejaswini', 'N/A', 'AI & DS Dept', 'admin'),
        ('admin_jagadish', 'admin123', 'Prof. Jagadish', 'N/A', 'ECE Dept', 'admin'),
        ('258p5a3006', 'pass123', 'Surya', '2025', 'Computer Science', 'student'),
        ('258p5a3008', 'pass123', 'Uday', '2025', 'Computer Science', 'student'),
        ('248p1a3078', 'pass123', 'Omkar', '2024', 'Mechanical Engineering', 'student')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', users_data)
    
    results_data = [('258p5a3006', 'Semester 1', 8.2), ('258p5a3006', 'Semester 2', 8.7), ('258p5a3006', 'Semester 3', 8.5), ('258p5a3006', 'Semester 4', 9.1)]
    cursor.executemany('INSERT INTO results (roll_number, semester, gpa) VALUES (?, ?, ?)', results_data)

    # NEW: Mock Attendance
    attendance_data = [
        ('258p5a3006', 150, 132, 88.0), # Surya has 88%
        ('258p5a3008', 150, 100, 66.6), # Uday has 66.6%
        ('248p1a3078', 150, 145, 96.6)  # Omkar has 96.6%
    ]
    cursor.executemany('INSERT INTO attendance VALUES (?, ?, ?, ?)', attendance_data)

    # NEW: Mock Curriculum (CSE Semester 5)
    curriculum_data = [
        ('Computer Science', 'Semester 5', 'CS501', 'Artificial Intelligence'),
        ('Computer Science', 'Semester 5', 'CS502', 'Computer Networks'),
        ('Computer Science', 'Semester 5', 'CS503', 'Database Management Systems')
    ]
    cursor.executemany('INSERT INTO curriculum (branch, semester, subject_code, subject_name) VALUES (?, ?, ?, ?)', curriculum_data)
    
    conn.commit()
    conn.close()
    print("Database updated with Attendance and Curriculum features!")

if __name__ == "__main__":
    setup_database()