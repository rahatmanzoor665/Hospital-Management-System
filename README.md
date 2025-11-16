# Hospital Management System (Python + Tkinter + MySQL)

A complete Hospital Management System (HMS) built with Python (Tkinter GUI) and MySQL database.
This application manages core hospital operations including patients, doctors, staff, appointments, rooms, billing, and user accounts with role-based access.

# Features

1. Secure Login System
Role-based authentication (Admin, Doctor, Reception, Nurse, Accountant)
Passwords stored using SHA-256 hashing
Admin-only access to user management module

2. Patient Management
Add, update, delete patient records
Store demographic, medical, and admission details
Assign doctor and room
Search patients by name or phone

3. Doctor Management
Maintain doctor profiles
Store specialization, contact info, and room number

4. Appointment Scheduler
Schedule new appointments
Update or cancel appointments
Track appointment status

5. Room Management
Add and manage rooms
Track room type, status (free/occupied), price per day
Assign patients to rooms

6. Billing System
Auto-calculate total cost: doctor + room + medicine + other charges
Track payment status (paid/unpaid/partial)
Store patient billing history

7. Staff Management
Manage nurses, technicians, receptionists, etc.
Track roles and work shifts

8. User Management (Admin Only)
Create system users
Assign user roles
Secure password storage

# Technologies Used
Component	Technology
Frontend GUI	Python Tkinter
Backend Logic	Python (OOP-based architecture)
Database	MySQL
Password Security	hashlib (SHA-256)
Data Communication	mysql-connector-python

# Project Structure
Hospital-Management-System/
│
├── hospital_app.py                         # Main application (Tkinter GUI)
├── Hospital_Database_Management_System_MYSQL.sql   # Database schema
├── README.md                               # Project documentation
└── /assets (optional for screenshots)

# Database Setup (MySQL)
Install MySQL Server
Open MySQL Workbench or CLI
Run the SQL file:
SOURCE Hospital_Database_Management_System_MYSQL.sql;
This will create:
Database: hospital_db
All tables (patients, doctors, staff, appointments, bills, etc.)
Default admin account:
username: admin
password: 12345

# Running the Application
1. Install Required Libraries
pip install mysql-connector-python
2. Configure Database Connection
Inside hospital_app.py, update this section if needed:
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'hospital_db'
}
3. Run the App
python hospital_app.py
The Tkinter GUI will launch.

# Screenshots
You can add your screenshots here:
![Login Page](assets/login.png)
![Dashboard](assets/dashboard.png)
Default Admin Credentials
Username	Password
admin	12345
You can change this later in the MySQL database.
Contribution
Contributions are welcome!
Fork the repository
Create a new branch
Commit your changes
Create a pull request
You may modify, distribute, or use the code for personal or commercial purposes.

Support
If you like this project, consider giving it a star ⭐ on GitHub!
