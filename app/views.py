from flask import Flask, render_template, request, redirect, url_for

import sqlite3
import pdfkit


app = Flask(__name__)

# Function to initialize database

def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, grade TEXT, branch TEXT, department TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS subjects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, subject_name TEXT, mark INTEGER)''')
    conn.commit()
    conn.close()

init_db()


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        # Validate that student_id is a valid integer
        try:
            student_id = int(student_id)
        except ValueError:
            # Handle case where student_id is not a valid integer
            return render_template('student/student_login.html', error_message="Student ID must be a valid integer.")

        # Redirect to student_dashboard with valid student_id
        return redirect(url_for('student_dashboard', student_id=student_id))
    
    # Render student login form
    return render_template('student/student_login.html')


@app.route('/student/dashboard/<int:student_id>')
def student_dashboard(student_id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('SELECT name, age FROM students WHERE id = ?', (student_id,))
    student_details = c.fetchone()
    conn.close()
    if student_details:
        student_name, student_age = student_details
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('SELECT subject_name, mark FROM subjects WHERE student_id = ?', (student_id,))
        subjects_with_marks = c.fetchall()
        conn.close()
        total_marks = sum(mark for _, mark in subjects_with_marks)
        aggregate_percentage = (total_marks / (len(subjects_with_marks) * 100)) * 100
        return render_template('student/student_dashboard.html', student_id=student_id, student_name=student_name, student_age=student_age, subjects_with_marks=subjects_with_marks, total_marks=total_marks, aggregate_percentage=aggregate_percentage)
    else:
        return render_template('error.html', error_message="Student details not found.")


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Your validation logic for admin login goes here
        # You can check if the username and password match the credentials stored in the database
        # Example: if username == 'admin' and password == 'admin':
        #            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/admin_login.html')



@app.route('/admin/dashboard')
def admin_dashboard():
    # Your logic for admin dashboard goes here
    return render_template('admin/admin_dashboard.html')
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        branch = request.form['branch']
        department = request.form['department']
        subjects = []
        marks = []
        for i in range(1, 6):
            subject = request.form.get(f'subject{i}', '')
            mark = request.form.get(f'mark{i}', '')
            if subject and mark:
                subjects.append(subject)
                marks.append(mark)
        
        # Connect to the database
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        
        # Create students table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS students
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, grade TEXT, branch TEXT, department TEXT)''')
        
        # Insert student details into students table
        c.execute('''INSERT INTO students (name, age, grade, branch, department) VALUES (?, ?, ?, ?, ?)''', (name, age, grade, branch, department))
        
        # Get the student id
        student_id = c.lastrowid
        
        # Create subjects table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS subjects
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, subject_name TEXT, mark INTEGER)''')
        
        # Insert subjects and marks into subjects table
        for i in range(len(subjects)):
            c.execute('''INSERT INTO subjects (student_id, subject_name, mark) VALUES (?, ?, ?)''', (student_id, subjects[i], marks[i]))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_students'))

    return render_template('admin/add_student.html')

@app.route('/admin/view_students')
def view_students():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()

    # Fetch subject marks for each student
    subjects = {}
    for student in students:
        student_id = student[0]
        c.execute('SELECT subject_name, mark FROM subjects WHERE student_id = ?', (student_id,))
        student_subjects = c.fetchall()
        subjects[student_id] = student_subjects

    conn.close()

    return render_template('admin/view_students.html', students=students, subjects=subjects)

@app.route('/admin/update_result/<int:student_id>', methods=['GET', 'POST'])
def update_result(student_id):
    if request.method == 'POST':
        # Fetch the updated marks for each subject from the form
        subject1_mark = request.form['subject1_mark']
        subject2_mark = request.form['subject2_mark']
        subject3_mark = request.form['subject3_mark']
        subject4_mark = request.form['subject4_mark']
        subject5_mark = request.form['subject5_mark']
        
        # Update the student's marks in the database
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('UPDATE subjects SET mark=? WHERE student_id=? AND subject_name=?',
                  (subject1_mark, student_id, 'subject1'))
        c.execute('UPDATE subjects SET mark=? WHERE student_id=? AND subject_name=?',
                  (subject2_mark, student_id, 'subject2'))
        c.execute('UPDATE subjects SET mark=? WHERE student_id=? AND subject_name=?',
                  (subject3_mark, student_id, 'subject3'))
        c.execute('UPDATE subjects SET mark=? WHERE student_id=? AND subject_name=?',
                  (subject4_mark, student_id, 'subject4'))
        c.execute('UPDATE subjects SET mark=? WHERE student_id=? AND subject_name=?',
                  (subject5_mark, student_id, 'subject5'))
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_students'))  # Redirect to view students page after updating
    else:
        # Fetch student details and marks from the database
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = c.fetchone()
        c.execute('SELECT subject_name, mark FROM subjects WHERE student_id = ?', (student_id,))
        subjects_with_marks = c.fetchall()
        conn.close()
        return render_template('admin/update_result.html', student=student, subjects_with_marks=subjects_with_marks)


@app.route('/admin/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if request.method == 'POST':
        # Connect to the database
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        
        # Delete the student from students table
        c.execute('DELETE FROM students WHERE id = ?', (student_id,))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_students'))




if __name__ == '__main__':
    app.run(debug=True,port=5026)
