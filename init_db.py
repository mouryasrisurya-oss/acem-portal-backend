import sqlite3

def setup_database():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # 1. Drop old tables to ensure a clean slate for the presentation
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS results')
    
    # 2. Create Tables
    cursor.execute('''
        CREATE TABLE users (
            roll_number TEXT PRIMARY KEY,
            password TEXT,
            name TEXT,
            batch_year TEXT,
            branch TEXT,
            role TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT,
            semester TEXT,
            gpa REAL
        )
    ''')

    cursor.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, issue_type TEXT, description TEXT, status TEXT DEFAULT "Pending")')
    cursor.execute('CREATE TABLE IF NOT EXISTS event_registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_number TEXT, event_name TEXT)')

    # 3. MOCK DATA: Admins & Students
    users_data = [
        # --- FACULTY / ADMINS ---
        ('admin_jahnavi', 'admin123', 'Prof. Jahnavi', 'N/A', 'CSE Dept', 'admin'),
        ('admin_tejaswini', 'admin123', 'Prof. Tejaswini', 'N/A', 'AI & DS Dept', 'admin'),
        ('admin_jagadish', 'admin123', 'Prof. Jagadish', 'N/A', 'ECE Dept', 'admin'),
        
        # --- STUDENTS ---
        ('258p5a3006', 'pass123', 'Surya', '2025', 'Computer Science', 'student'),
        ('258p5a3008', 'pass123', 'Uday', '2025', 'Computer Science', 'student'),
        ('248p1a3078', 'pass123', 'Omkar', '2024', 'Mechanical Engineering', 'student'),
        ('248p1a30a0', 'pass123', 'Pavan', '2024', 'Civil Engineering', 'student')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', users_data)
    
    # 4. MOCK DATA: GPA Analytics for Charts
    results_data = [
        # Surya's Grades
        ('258p5a3006', 'Semester 1', 8.2), ('258p5a3006', 'Semester 2', 8.7),
        ('258p5a3006', 'Semester 3', 8.5), ('258p5a3006', 'Semester 4', 9.1),
        # Uday's Grades
        ('258p5a3008', 'Semester 1', 7.5), ('258p5a3008', 'Semester 2', 7.8),
        ('258p5a3008', 'Semester 3', 8.1), ('258p5a3008', 'Semester 4', 8.4),
        # Omkar's Grades
        ('248p1a3078', 'Semester 3', 6.9), ('248p1a3078', 'Semester 4', 7.2),
        ('248p1a3078', 'Semester 5', 7.9), ('248p1a3078', 'Semester 6', 8.0),
        # Pavan's Grades
        ('248p1a30a0', 'Semester 3', 8.8), ('248p1a30a0', 'Semester 4', 9.0),
        ('248p1a30a0', 'Semester 5', 8.9), ('248p1a30a0', 'Semester 6', 9.2)
    ]
    cursor.executemany('INSERT INTO results (roll_number, semester, gpa) VALUES (?, ?, ?)', results_data)
    
    conn.commit()
    conn.close()
    print("ACEM Database successfully built with Faculty and Student records!")

if __name__ == "__main__":
    setup_database()