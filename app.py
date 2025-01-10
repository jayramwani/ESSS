from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
import random
import logging
import os

from database import create_connection, insert_user, get_user  # Import database functions

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Flask-Mail using environment variables
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Use environment variable
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Use environment variable
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')  # Use environment variable

mail = Mail(app)

# In-memory storage for OTP
otp_storage = {}

@app.route('/')  # Route for the root URL
def home():
    return "Welcome to the Login API! Use /api/login to log in, /api/requestOtp to request an OTP, and /api/register to register a new user."

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(success=False, message='Email and password are required'), 400

    if insert_user(email, password):
        return jsonify(success=True, message='User registered successfully'), 201
    else:
        return jsonify(success=False, message='User already exists'), 409  # Conflict

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = get_user(email, password)

    if user:
        otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
        otp_storage[email] = otp  # Store OTP in memory
        send_otp(email, otp)  # Send OTP to the user's email
        return jsonify(success=True, message='OTP sent to your email')
    else:
        return jsonify(success=False, message='Invalid email or password'), 401

@app.route('/api/requestOtp', methods=['POST'])
def request_otp():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify(success=False, message='Email is required'), 400

    # Generate a 6-digit OTP
    otp = random.randint(100000, 999999)
    otp_storage[email] = otp  # Store OTP in memory
    send_otp(email, otp)  # Send OTP to the user's email
    return jsonify(success=True, message='OTP sent to your email')

def send_otp(email, otp):
    logging.debug(f"Sending OTP {otp} to {email}")
    msg = Message('Your OTP Code', recipients=[email])
    msg.body = f'Your OTP code is { otp}'
    try:
        mail.send(msg)
        logging.info(f"OTP sent successfully to {email}")
    except Exception as e:
        logging.error(f"Failed to send OTP: {str(e)}")
        logging.error("Check your email configuration and credentials.")

@app.route('/api/verifyOtp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify(success=False, message='Email and OTP are required'), 400

    if email in otp_storage and otp_storage[email] == otp:
        del otp_storage[email]  # Remove OTP after verification
        return jsonify(success=True, message='OTP verified successfully')
    else:
        return jsonify(success=False, message='Invalid OTP'), 401

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, request, jsonify
# from flask_mail import Mail, Message
# from flask_cors import CORS
# import random
# import sqlite3
# import logging
# import os
# import threading
# import requests  # Import requests to send HTTP requests

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Initialize the Flask application
# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Configure Flask-Mail using environment variables
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Use environment variable
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Use environment variable
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')  # Use environment variable

# mail = Mail(app)

# # In-memory storage for OTP and PIN
# otp_storage = {}
# pin_storage = {}

# def create_connection():
#     conn = sqlite3.connect('users.db')
#     return conn

# @app.route('/')  # Route for the root URL
# def home():
#     return "Welcome to the Login API! Use /api/login to log in, /api/requestOtp to request an OTP, and /api/sendPin to generate a PIN."

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')

#     # Validate the email and password against the database
#     conn = create_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
#     user = cursor.fetchone()
#     conn.close()

#     if user:
#         otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
#         otp_storage[email] = otp  # Store OTP in memory
#         send_otp(email, otp)  # Send OTP to the user's email
#         return jsonify(success=True, message='OTP sent to your email')
#     else:
#         return jsonify(success=False, message='Invalid email or password'), 401

# @app.route('/api/requestOtp', methods=['POST'])
# def request_otp():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify(success=False, message='Email is required'), 400

#     # Generate a 6-digit OTP
#     otp = random.randint(100000, 999999)
#     otp_storage[email] = otp  # Store OTP in memory
#     send_otp(email, otp) 
#     # Send OTP to the user's email
#     return jsonify(success=True, message='OTP sent to your email')

# def send_otp(email, otp):
#     logging.debug(f"Sending OTP {otp} to {email}")
#     msg = Message('Your OTP Code', recipients=[email])
#     msg.body = f'Your OTP code is {otp}'
#     try:
#         mail.send(msg)
#         logging.info(f"OTP sent successfully to {email}")
#     except Exception as e:
#         logging.error(f"Failed to send OTP: {str(e)}")
#         logging.error("Check your email configuration and credentials.")

# @app.route('/api/verifyOtp', methods=['POST'])
# def verify_otp():
#     data = request.get_json()
#     email = data.get('email')
#     otp = data.get('otp')

#     logging.debug(f"Received OTP for {email}: {otp}")
#     logging.debug(f"Stored OTP for {email}: {otp_storage.get(email)}")

#     # Verify the OTP
#     if email in otp_storage and otp_storage[email] == int(otp):
#         del otp_storage[email]  # Remove OTP after verification
#         logging.info(f"OTP verified successfully for {email}")
#         return jsonify(success=True, message='OTP verified successfully', verified=True)
#     else:
#         logging.warning(f"Invalid OTP attempt for {email}: {otp}")
#         return jsonify(success=False, message='Invalid OTP', verified=False), 400

# @app.route('/api/sendPin', methods=['POST'])
# def send_pin():
#     data = request.get_json()
#     logging.debug(f"Received data: {data}")  # Log the incoming data
#     email = data.get('email')
#     pin = data.get('pin')

#     if not email or not pin:
#         return jsonify(success=False, message='Email and PIN are required'), 400

#     # Store the PIN in memory
#     pin_storage[email] = pin  # Store PIN in memory
#     logging.info(f"Received PIN {pin} for {email}")

#     # Send the PIN to NodeMCU ESP32
#     esp32_url = "http://<192.168.1.100>/receivePin"  # Replace with your ESP32's IP address
#     try:
#         response = requests.post(esp32_url, json={'email': email, 'pin': pin})
#         if response.status_code == 200:
#             logging.info(f"PIN {pin} sent to ESP32 successfully.")
#         else:
#             logging.error(f"Failed to send PIN to ESP32: {response.text}")
#     except Exception as e:
#         logging.error(f"Error sending PIN to ESP32: {str(e)}")

#     return jsonify(success=True, message='PIN received successfully')

# def expire_pin(email):
#     if email in pin_storage:
#         del pin_storage[email]  # Remove PIN after expiration
#         logging.info(f"PIN for {email} has expired and has been removed.")

# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, request, jsonify
# from flask_mail import Mail, Message
# from flask_cors import CORS
# import random
# import sqlite3
# import logging
# import os
# import threading
# import requests  # Import requests to send HTTP requests

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Initialize the Flask application
# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Configure Flask-Mail using environment variables
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Use environment variable
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Use environment variable
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')  # Use environment variable

# mail = Mail(app)

# # In-memory storage for OTP and PIN
# otp_storage = {}
# pin_storage = {}

# def create_connection():
#     conn = sqlite3.connect('users.db')
#     return conn

# @app.route('/')  # Route for the root URL
# def home():
#     return "Welcome to the Login API! Use /api/login to log in, /api/requestOtp to request an OTP, and /api/sendPin to generate a PIN."

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')

#     # Validate the email and password against the database
#     conn = create_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
#     user = cursor.fetchone()
#     conn.close()

#     if user:
#         otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
#         otp_storage[email] = otp  # Store OTP in memory
#         send_otp(email, otp)  # Send OTP to the user's email
#         return jsonify(success=True, message='OTP sent to your email')
#     else:
#         return jsonify(success=False, message='Invalid email or password'), 401

# @app.route('/api/requestOtp', methods=['POST'])
# def request_otp():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify(success=False, message='Email is required'), 400

#     # Generate a 6-digit OTP
#     otp = random.randint(100000, 999999)
#     otp_storage[email] = otp  # Store OTP in memory
#     send_otp(email, otp)  # Send OTP to the user's email

#     return jsonify(success=True, message='OTP sent to your email')

# def send_otp(email, otp):
#     logging.debug(f"Sending OTP {otp} to {email}")
#     msg = Message('Your OTP Code', recipients=[email])
#     msg.body = f'Your OTP code is {otp}'
#     try:
#         mail.send(msg)
#         logging.info(f"OTP sent successfully to {email}")
#     except Exception as e:
#         logging.error(f"Failed to send OTP: {str(e)}")
#         logging.error("Check your email configuration and credentials.")

# @app.route('/api/verifyOtp', methods=['POST'])
# def verify_otp():
#     data = request.get_json()
#     email = data.get('email')
#     otp = data.get('otp')

#     logging.debug(f"Received OTP for {email}: {otp}")
#     logging.debug(f"Stored OTP for {email}: {otp_storage.get(email)}")

#     # Verify the OTP
#     if email in otp_storage and otp_storage[email] == int(otp):
#         del otp_storage[email]  # Remove OTP after verification
#         logging.info(f"OTP verified successfully for {email}")
#         return jsonify(success=True, message='OTP verified successfully', verified=True)
#     else:
#         logging.warning(f"Invalid OTP attempt for {email}: {otp}")
#         return jsonify(success=False, message='Invalid OTP', verified=False), 400

# @app.route('/api/sendPin', methods=['POST'])
# def send_pin():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify(success=False, message='Email is required'), 400

#     # Generate a 6-digit PIN
#     pin = random.randint(100000, 999999)
#     pin_storage[email] = pin  # Store PIN in memory

#     # Send the PIN to the NodeMCU ESP32
#     send_pin_to_esp32(pin)

#     # Start a timer to expire the PIN after 5 minutes
#     threading.Timer(300, expire_pin, args=[email]).start()

#     logging.info(f"Generated PIN {pin} for {email}")
#     return jsonify(success=True, message='PIN generated successfully', pin=pin)

# def send_pin_to_esp32(pin):
#     esp32_url = f'http://192.168.1.100/receivePin?pin={pin}'  # Use the static IP address
#     try:
#         response = requests.get(esp32_url)
#         if response.status_code == 200:
#             logging.info(f"PIN {pin} sent to ESP32 successfully.")
#         else:
#             logging.error(f"Failed to send PIN to ESP32: {response.text}")
#     except Exception as e:
#         logging.error(f"Error sending PIN to ESP32: {str(e)}")

# def expire_pin(email):
#     if email in pin_storage:
#         del pin_storage[email]  # Remove PIN after expiration
#         logging.info(f"PIN for {email} has expired and has been removed.")

# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, request, jsonify
# from flask_mail import Mail, Message
# from flask_cors import CORS
# import random
# import sqlite3
# import logging
# import os
# import time
# import threading

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Initialize the Flask application
# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Configure Flask-Mail using environment variables
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Use environment variable
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Use environment variable
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')  # Use environment variable

# mail = Mail(app)

# # In-memory storage for OTP and PIN
# otp_storage = {}
# pin_storage = {}

# def create_connection():
#     conn = sqlite3.connect('users.db')
#     return conn

# @app.route('/')  # Route for the root URL
# def home():
#     return "Welcome to the Login API! Use /api/login to log in and /api/verifyOtp to verify OTP."

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')

#     # Validate the email and password against the database
#     conn = create_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
#     user = cursor.fetchone()
#     conn.close()

#     if user:
#         otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
#         otp_storage[email] = otp  # Store OTP in memory
#         send_otp(email, otp)  # Send OTP to the user's email
#         return jsonify(success=True, message='OTP sent to your email')
#     else:
#         return jsonify(success=False, message='Invalid email or password'), 401

# @app.route('/api/requestOtp', methods=['POST'])
# def request_otp():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify(success=False, message='Email is required'), 400

#     # Generate a 6-digit OTP
#     otp = random.randint(100000, 999999)
#     otp_storage[email] = otp  # Store OTP in memory
#     send_otp(email, otp)  # Send OTP to the user's email

#     return jsonify(success=True, message='OTP sent to your email')

# def send_otp(email, otp):
#     logging.debug(f"Sending OTP {otp} to {email}")
#     msg = Message('Your OTP Code', recipients=[email])
#     msg.body = f'Your OTP code is {otp}'
#     try:
#         mail.send(msg)
#         logging.info(f"OTP sent successfully to {email}")
#     except Exception as e:
#         logging.error(f"Failed to send OTP: {str(e)}")
#         logging.error("Check your email configuration and credentials.")

# @app.route('/api/verifyOtp', methods=['POST'])
# def verify_otp():
#     data = request.get_json()
#     email = data.get('email')
#     otp = data.get('otp')

#     logging.debug(f"Received OTP for {email}: {otp}")
#     logging.debug(f"Stored OTP for {email}: {otp_storage.get(email)}")

#     # Verify the OTP
#     if email in otp_storage and otp_storage[email] == int(otp):
#         del otp_storage[email]  # Remove OTP after verification
#         logging.info(f"OTP verified successfully for {email}")
#         return jsonify(success=True, message='OTP verified successfully', verified=True)
#     else:
#         logging.warning(f"Invalid OTP attempt for {email}: {otp}")
#         return jsonify(success=False, message='Invalid OTP', verified=False), 400

# @app.route('/api/generatePin', methods=['POST'])
# def generate_pin():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify(success=False, message='Email is required'), 400

#     # Generate a 6-digit PIN
#     pin = random.randint(100000, 999999)
#     pin_storage[email] = pin  # Store PIN in memory

#     # Send the PIN to the user's email (optional)
#     send_pin(email, pin)

#     # Start a timer to expire the PIN after 5 minutes
#     threading.Timer(300, expire_pin, args=[email]).start()

#     return jsonify(success=True, message='PIN generated and sent to your email', pin=pin)

# def send_pin(email, pin):
#     logging.debug(f"Sending PIN {pin} to {email}")
#     msg = Message('Your PIN Code', recipients=[email])
#     msg.body = f'Your PIN code is {pin}'
#     try:
#         mail.send(msg)
#         logging.info(f"PIN sent successfully to {email}")
#     except Exception as e:
#         logging.error(f"Failed to send PIN: {str(e)}")
#         logging.error("Check your email configuration and credentials.")

# def expire_pin(email):
#     if email in pin_storage:
#         del pin_storage[email]  # Remove PIN after expiration
#         logging.info(f"PIN for {email} has expired and has been removed.")

# if __name__ == '__main__':
#     app.run(debug=True)
