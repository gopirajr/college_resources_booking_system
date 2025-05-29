from flask import Flask, render_template, request, redirect
from db_config import init_mysql
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
mysql = init_mysql(app)

@app.route('/')
def home():
    return redirect('/resources')

@app.route('/resources')
def list_resources():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM resources")
    resources = cur.fetchall()
    return render_template('resources.html', resources=resources)

@app.route('/book/<int:resource_id>', methods=['GET', 'POST'])
def book_resource(resource_id):
    if request.method == 'POST':
        data = (
            request.form['student_name'],
            request.form['email'],
            resource_id,
            request.form['date'],
            request.form['start_time'],
            request.form['end_time'],
            request.form['reason']
        )
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO bookings (student_name, email, resource_id, date, start_time, end_time, reason, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
        """, data)
        mysql.connection.commit()
        return redirect('/booking_status?email=' + data[1])
    return render_template('book_resource.html', resource_id=resource_id)

@app.route('/booking_status')
def booking_status():
    email = request.args.get('email')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT b.*, r.name FROM bookings b
        JOIN resources r ON b.resource_id = r.resource_id
        WHERE b.email = %s
        ORDER BY date DESC
    """, (email,))
    bookings = cur.fetchall()
    return render_template('booking_status.html', bookings=bookings)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        status = request.form['status']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE bookings SET status = %s WHERE booking_id = %s", (status, booking_id))
        mysql.connection.commit()

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT b.*, r.name FROM bookings b
        JOIN resources r ON b.resource_id = r.resource_id
        ORDER BY date DESC
    """)
    records = cur.fetchall()
    return render_template('admin_dashboard.html', bookings=records)

if __name__ == '__main__':
    app.run(debug=True)
