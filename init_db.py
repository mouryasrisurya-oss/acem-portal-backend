import sqlite3

def setup_database():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    tables = ['users', 'results', 'attendance', 'curriculum', 'reports', 'event_registrations', 'campus_events', 'fest_registrations']
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
    
    # NEW: Added phone and blood_group to the users table
    cursor.execute('''
        CREATE TABLE users (
            roll_number TEXT PRIMARY KEY, password TEXT, name TEXT, 
            batch_year TEXT, branch TEXT, role TEXT, phone TEXT, blood_group TEXT
        )
    ''')
    
    cursor.execute('CREATE TABLE results (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, semester TEXT, gpa REAL)')
    cursor.execute('CREATE TABLE attendance (roll_number TEXT PRIMARY KEY, total_classes INTEGER, attended_classes INTEGER, percentage REAL)')
    cursor.execute('CREATE TABLE curriculum (id INTEGER PRIMARY KEY AUTOINCREMENT, branch TEXT, semester TEXT, subject_code TEXT, subject_name TEXT, subject_type TEXT)')
    cursor.execute('CREATE TABLE reports (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, issue_type TEXT, description TEXT, status TEXT DEFAULT "Pending")')
    cursor.execute('CREATE TABLE event_registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, event_title TEXT)')
    cursor.execute('CREATE TABLE campus_events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date TEXT, description TEXT, faculty TEXT, contact TEXT)')
    cursor.execute('CREATE TABLE fest_registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, name TEXT, branch TEXT, payment_type TEXT)')

    # Added default phone and blood groups for our mock data
    users_data = [
        ('admin_jahnavi', 'admin123', 'Prof. Jahnavi', 'N/A', 'CSE Dept', 'admin', 'N/A', 'N/A'),
        ('admin_tejaswini', 'admin123', 'Prof. Tejaswini', 'N/A', 'AI & DS Dept', 'admin', 'N/A', 'N/A'),
        ('admin_jagadish', 'admin123', 'Prof. Jagadish', 'N/A', 'ECE Dept', 'admin', 'N/A', 'N/A'),
        ('248p1a3078', 'pass123', 'Omkar', '2024', 'Mechanical Engineering', 'student', '9876543210', 'O+'),
        ('248p1a30a0', 'pass123', 'Pavan', '2024', 'Civil Engineering', 'student', '9876543211', 'A+'),
        ('258p5a3006', 'pass123', 'Surya', '2025', 'Computer Science', 'student', '9876543212', 'B+'),
        ('258p5a3008', 'pass123', 'Uday', '2025', 'Computer Science', 'student', '9876543213', 'AB+'),
        ('268p1a3012', 'pass123', 'Ananya', '2026', 'Artificial Intelligence', 'student', '9876543214', 'O-'),
        ('268p1a3045', 'pass123', 'Karthik', '2026', 'Electronics (ECE)', 'student', '9876543215', 'A-')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)', users_data)
    
    # GPA & Attendance Data
    cursor.executemany('INSERT INTO results (roll_number, semester, gpa) VALUES (?, ?, ?)', [
        ('258p5a3006', 'Semester 1', 8.2), ('258p5a3006', 'Semester 2', 8.7), ('258p5a3006', 'Semester 3', 8.5), ('258p5a3006', 'Semester 4', 9.1),
        ('258p5a3008', 'Semester 1', 7.1), ('258p5a3008', 'Semester 2', 7.4), ('258p5a3008', 'Semester 3', 7.8), ('258p5a3008', 'Semester 4', 8.2)
    ])
    cursor.executemany('INSERT INTO attendance VALUES (?, ?, ?, ?)', [('258p5a3006', 150, 132, 88.0), ('258p5a3008', 150, 100, 66.6)])

    # Core CSE Sem 5 Curriculum
    cursor.executemany('INSERT INTO curriculum (branch, semester, subject_code, subject_name, subject_type) VALUES (?, ?, ?, ?, ?)', [
        ('Computer Science', 'Semester 5', 'CS501', 'Artificial Intelligence', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS502', 'Computer Networks', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS503', 'Database Management Systems', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS507L', 'Artificial Intelligence Lab', 'Lab')
    ])

    # Events & Fests
    cursor.executemany('INSERT INTO campus_events (title, date, description, faculty, contact) VALUES (?, ?, ?, ?, ?)', [
        ('Cybersecurity Workshop', 'Nov 15', 'Practical vulnerability assessment.', 'Prof. Jahnavi', 'jahnavi@acem.edu')
    ])
    cursor.executemany('INSERT INTO event_registrations (roll_number, event_title) VALUES (?, ?)', [('258p5a3008', 'Cybersecurity Workshop')])
    cursor.executemany('INSERT INTO fest_registrations (roll_number, name, branch, payment_type) VALUES (?, ?, ?, ?)', [('258p5a3008', 'Uday', 'Computer Science', 'PhonePe')])
    cursor.executemany('INSERT INTO reports (roll_number, issue_type, description, status) VALUES (?, ?, ?, ?)', [('258p5a3008', 'Bus/Transport', 'Bus 4 late.', 'Pending')])

    conn.commit()
    conn.close()
    print("Database built with Dynamic Students and Profile functionality!")

if __name__ == "__main__":
    setup_database()