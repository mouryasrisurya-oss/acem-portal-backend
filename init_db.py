import sqlite3

def setup_database():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # 1. Reset Tables (Guarantees a clean slate every time you run this)
    tables = [
        'users', 'results', 'attendance', 'curriculum', 
        'reports', 'event_registrations', 'campus_events', 'fest_registrations'
    ]
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
    
    # 2. Create Tables
    cursor.execute('CREATE TABLE users (roll_number TEXT PRIMARY KEY, password TEXT, name TEXT, batch_year TEXT, branch TEXT, role TEXT)')
    cursor.execute('CREATE TABLE results (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, semester TEXT, gpa REAL)')
    cursor.execute('CREATE TABLE attendance (roll_number TEXT PRIMARY KEY, total_classes INTEGER, attended_classes INTEGER, percentage REAL)')
    
    # Notice the new 'subject_type' column here for Theory vs Lab!
    cursor.execute('CREATE TABLE curriculum (id INTEGER PRIMARY KEY AUTOINCREMENT, branch TEXT, semester TEXT, subject_code TEXT, subject_name TEXT, subject_type TEXT)')
    
    cursor.execute('CREATE TABLE reports (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, issue_type TEXT, description TEXT, status TEXT DEFAULT "Pending")')
    cursor.execute('CREATE TABLE event_registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, event_title TEXT)')
    cursor.execute('CREATE TABLE campus_events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date TEXT, description TEXT, faculty TEXT, contact TEXT)')
    cursor.execute('CREATE TABLE fest_registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, name TEXT, branch TEXT, payment_type TEXT)')

    # 3. Admins & Students Roster
    users_data = [
        ('admin_jahnavi', 'admin123', 'Prof. Jahnavi', 'N/A', 'CSE Dept', 'admin'),
        ('admin_tejaswini', 'admin123', 'Prof. Tejaswini', 'N/A', 'AI & DS Dept', 'admin'),
        ('admin_jagadish', 'admin123', 'Prof. Jagadish', 'N/A', 'ECE Dept', 'admin'),
        ('248p1a3078', 'pass123', 'Omkar', '2024', 'Mechanical Engineering', 'student'),
        ('248p1a30a0', 'pass123', 'Pavan', '2024', 'Civil Engineering', 'student'),
        ('258p5a3006', 'pass123', 'Surya', '2025', 'Computer Science', 'student'),
        ('258p5a3008', 'pass123', 'Uday', '2025', 'Computer Science', 'student'),
        ('268p1a3012', 'pass123', 'Ananya', '2026', 'Artificial Intelligence', 'student'),
        ('268p1a3045', 'pass123', 'Karthik', '2026', 'Electronics (ECE)', 'student')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', users_data)
    
    # 4. GPA Data
    results_data = [
        ('258p5a3006', 'Semester 1', 8.2), ('258p5a3006', 'Semester 2', 8.7), ('258p5a3006', 'Semester 3', 8.5), ('258p5a3006', 'Semester 4', 9.1),
        ('258p5a3008', 'Semester 1', 7.1), ('258p5a3008', 'Semester 2', 7.4), ('258p5a3008', 'Semester 3', 7.8), ('258p5a3008', 'Semester 4', 8.2),
        ('248p1a3078', 'Semester 1', 6.5), ('248p1a3078', 'Semester 2', 6.8), ('248p1a3078', 'Semester 3', 7.0), ('248p1a3078', 'Semester 4', 7.2)
    ]
    cursor.executemany('INSERT INTO results (roll_number, semester, gpa) VALUES (?, ?, ?)', results_data)

    # 5. Attendance Data
    attendance_data = [
        ('258p5a3006', 150, 132, 88.0),
        ('258p5a3008', 150, 100, 66.6),
        ('248p1a3078', 150, 145, 96.6) 
    ]
    cursor.executemany('INSERT INTO attendance VALUES (?, ?, ?, ?)', attendance_data)

    # 6. Theory & Lab Curriculum Data
    curriculum_data = [
        ('Computer Science', 'Semester 5', 'CS501', 'Artificial Intelligence', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS502', 'Computer Networks', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS503', 'Database Management Systems', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS504', 'Formal Languages and Automata', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS505', 'Software Engineering', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS506', 'Web Technologies', 'Theory'),
        ('Computer Science', 'Semester 5', 'CS507L', 'Artificial Intelligence Lab', 'Lab'),
        ('Computer Science', 'Semester 5', 'CS508L', 'Database Management Systems Lab', 'Lab'),
        ('Computer Science', 'Semester 5', 'CS509L', 'Web Technologies Lab', 'Lab')
    ]
    cursor.executemany('INSERT INTO curriculum (branch, semester, subject_code, subject_name, subject_type) VALUES (?, ?, ?, ?, ?)', curriculum_data)

    # 7. Campus Events & Event Registrations
    cursor.executemany('INSERT INTO campus_events (title, date, description, faculty, contact) VALUES (?, ?, ?, ?, ?)', [
        ('Cybersecurity Workshop', 'Nov 15', 'Practical vulnerability assessment.', 'Prof. Jahnavi', 'jahnavi@acem.edu'),
        ('Data Science Hackathon', 'Nov 22', 'Build a Recommender System.', 'Prof. Tejaswini', 'tejaswini@acem.edu')
    ])
    cursor.executemany('INSERT INTO event_registrations (roll_number, event_title) VALUES (?, ?)', [
        ('258p5a3008', 'Cybersecurity Workshop'), ('268p1a3012', 'Data Science Hackathon'), ('248p1a3078', 'Data Science Hackathon')
    ])

    # 8. Tech Fest Registrations & Mock Reports
    cursor.executemany('INSERT INTO fest_registrations (roll_number, name, branch, payment_type) VALUES (?, ?, ?, ?)', [
        ('258p5a3008', 'Uday', 'Computer Science', 'PhonePe'),
        ('248p1a3078', 'Omkar', 'Mechanical Engineering', 'Cash'),
        ('268p1a3012', 'Ananya', 'Artificial Intelligence', 'GooglePay')
    ])
    cursor.executemany('INSERT INTO reports (roll_number, issue_type, description, status) VALUES (?, ?, ?, ?)', [
        ('258p5a3008', 'Bus/Transport', 'The route 4 bus was 30 minutes late today.', 'Pending'),
        ('268p1a3045', 'Hostel', 'Wi-Fi is not working on the 3rd floor.', 'Pending')
    ])

    conn.commit()
    conn.close()
    print("Database perfectly built with Curriculum, Fest, and Campus Roster!")

if __name__ == "__main__":
    setup_database()