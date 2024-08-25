from flask import Flask, request, jsonify
from dotenv import load_dotenv
import sqlite3
from twilio.rest import Client
import os

app = Flask(__name__)

load_dotenv()

# Twilio configuration (replace with your actual Twilio account SID, Auth Token, and Twilio number)
account_sid=os.getenv('account_sid')
auth_token=os.getenv('auth_token')
twilio_phone_number=os.getenv('twilio_phone_number')

client = Client(account_sid, auth_token)

# Function to retrieve student information from the SQLite database
def get_student_info(phone):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE phone=?", (phone,))
    student = cursor.fetchone()
    conn.close()
    return student

# Function to send SMS via Twilio
def send_sms(to_phone, message):
    client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=to_phone
    )
    # write something
def hello():
    print("hi")

@app.route('/missed_call', methods=['POST'])
def missed_call():
    if 'phone' not in request.form:
        return jsonify({"status": "error", "message": "Phone number is missing"}), 400
    
    # Get the phone number as an integer and format it for SMS
    phone_number = int(request.form['phone'])
    phone_db = str(phone_number) # Use integer for database query
    phone_sms = f"+91{phone_number}"  # Format for SMS
    
    student = get_student_info(phone_db)
    
    if student:
        name, fees_due, results, attendance = student[1], student[2], student[3], student[4]
        message = f"Name: {name}\nFees Due: {fees_due}\nResults: {results}\nAttendance: {attendance}"
        send_sms(phone_sms, message)
        return jsonify({"status": "success", "message": "Information sent via SMS"}), 200
    else:
        # Student not found, send an informative SMS
        message = "Student information not found. Please contact the college administration."
        send_sms(phone_sms, message)
        return jsonify({"status": "error", "message": "Student not found, message sent to parent"}), 404

if __name__ == '__main__':
    app.run(debug=True)