import os
from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "student_portal_secret"


# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "root"),
        database=os.environ.get("DB_NAME", "student_db")
    )

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'vit' and password == 'vit123456':
            session['logged_in'] = True
            return redirect('/dashboard')

        return render_template(
            'login.html',
            error="Invalid username or password!"
        )

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
    departments = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template(
        'dashboard.html',
        students=students,
        departments=departments
    )


# Add Student
@app.route('/add', methods=['POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect('/')

    name = request.form['name']
    department = request.form['department']
    email = request.form['email']

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
    INSERT INTO students (name, department, email)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (name, department, email))
    db.commit()

    cursor.close()
    db.close()

    return redirect('/dashboard')


# Delete Student
@app.route('/delete/<int:id>')
def delete_student(id):
    if not session.get('logged_in'):
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    db.commit()

    cursor.close()
    db.close()

    return redirect('/dashboard')


# Edit Student
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if not session.get('logged_in'):
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        email = request.form['email']

        cursor.execute(
            "UPDATE students SET name=%s, department=%s, email=%s WHERE id=%s",
            (name, department, email, id)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect('/dashboard')

    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('edit.html', student=student)


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)