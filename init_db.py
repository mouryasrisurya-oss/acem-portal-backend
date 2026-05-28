import sqlite3

def setup_database():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # 1. Reset Tables
    tables = ['users', 'results', 'attendance', 'curriculum', 'reports', 'event_registrations', 'campus_events']
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
    
    # 2. Create Tables
    cursor.execute('CREATE TABLE users (roll_number TEXT PRIMARY KEY, password TEXT, name TEXT, batch_year TEXT, branch TEXT, role TEXT)')
    cursor.execute('CREATE TABLE results (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, semester TEXT, gpa REAL)')
    cursor.execute('CREATE TABLE attendance (roll_number TEXT PRIMARY KEY, total_classes INTEGER, attended_classes INTEGER, percentage REAL)')
    cursor.execute('CREATE TABLE curriculum (id INTEGER PRIMARY KEY AUTOINCREMENT, branch TEXT, semester TEXT, subject_code TEXT, subject_name TEXT)')
    cursor.execute('CREATE TABLE reports (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, issue_type TEXT, description TEXT, status TEXT DEFAULT "Pending")')
    cursor.execute('CREATE TABLE event_registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, event_title TEXT)')
    
    # NEW: Dynamic Events Table
    cursor.execute('''
        CREATE TABLE campus_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT,
            description TEXT,
            faculty TEXT,
            contact TEXT
        )
    ''')

    # 3. Insert Mock Data (Users, Results, Attendance, Curriculum)
    users_data = [
        ('admin_jahnavi', 'admin123', 'Prof. Jahnavi', 'N/A', 'CSE Dept', 'admin'),
        ('admin_tejaswini', 'admin123', 'Prof. Tejaswini', 'N/A', 'AI & DS Dept', 'admin'),
        ('258p5a3006', 'pass123', 'Surya', '2025', 'Computer Science', 'student'),
        ('258p5a3008', 'pass123', 'Uday', '2025', 'Computer Science', 'student')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', users_data)
    
    cursor.executemany('INSERT INTO results (roll_number, semester, gpa) VALUES (?, ?, ?)', [
        ('258p5a3006', 'Semester 1', 8.2), ('258p5a3006', 'Semester 2', 8.7), ('258p5a3006', 'Semester 3', 8.5), ('258p5a3006', 'Semester 4', 9.1)
    ])
    cursor.executemany('INSERT INTO attendance VALUES (?, ?, ?, ?)', [('258p5a3006', 150, 132, 88.0)])
    cursor.executemany('INSERT INTO curriculum (branch, semester, subject_code, subject_name) VALUES (?, ?, ?, ?)', [
        ('Computer Science', 'Semester 5', 'CS501', 'Artificial Intelligence')
    ])

    # 4. NEW: Insert Default Dynamic Events
    events_data = [
        ('Cybersecurity Workshop', 'Nov 15', 'Learn practical vulnerability assessment techniques.', 'Prof. Jahnavi', 'jahnavi.cse@acem.edu'),
        ('Data Science Hackathon', 'Nov 22', 'Build a Recommender System in 24 hours.', 'Prof. Tejaswini', 'tejaswini.ai@acem.edu')
    ]
    cursor.executemany('INSERT INTO campus_events (title, date, description, faculty, contact) VALUES (?, ?, ?, ?, ?)', events_data)

    # 5. NEW: Add a mock registration so Admins have data to see
    cursor.execute('INSERT INTO event_registrations (roll_number, event_title) VALUES (?, ?)', ('258p5a3008', 'Cybersecurity Workshop'))

    conn.commit()
    conn.close()
    print("Database updated with Dynamic Events Manager!")

if __name__ == "__main__":
    setup_database()