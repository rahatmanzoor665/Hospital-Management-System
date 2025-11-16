CREATE DATABASE hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE hospital_db;
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(128) NOT NULL,
  role ENUM('admin','reception','doctor','account','nurse') NOT NULL DEFAULT 'reception',
  full_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patients (
  patient_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  gender ENUM('Male','Female','Other') DEFAULT 'Other',
  dob DATE,
  age INT,
  phone VARCHAR(20),
  address VARCHAR(255),
  disease VARCHAR(255),
  admit_date DATE,
  discharge_date DATE,
  doctor_id INT,
  room_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX (full_name),
  INDEX (phone)
);

CREATE TABLE doctors (
  doctor_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  specialization VARCHAR(100),
  phone VARCHAR(20),
  email VARCHAR(100),
  room_no VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE  staff (
  staff_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  role VARCHAR(50),
  phone VARCHAR(20),
  shift VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rooms (
  room_id INT AUTO_INCREMENT PRIMARY KEY,
  room_no VARCHAR(50) NOT NULL UNIQUE,
  type ENUM('General','Private','ICU','Semi-Private') DEFAULT 'General',
  status ENUM('free','occupied','maintenance') DEFAULT 'free',
  current_patient_id INT NULL,
  price_per_day DECIMAL(10,2) DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
  appointment_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  doctor_id INT,
  appt_date DATE NOT NULL,
  appt_time TIME,
  status ENUM('scheduled','completed','cancelled') DEFAULT 'scheduled',
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
);

CREATE TABLE bills (
  bill_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  doctor_charge DECIMAL(10,2) DEFAULT 0.00,
  room_charge DECIMAL(10,2) DEFAULT 0.00,
  medicine_charge DECIMAL(10,2) DEFAULT 0.00,
  other_charge DECIMAL(10,2) DEFAULT 0.00,
  total_amount DECIMAL(12,2) AS (doctor_charge + room_charge + medicine_charge + other_charge) STORED,
  payment_status ENUM('unpaid','paid','partial') DEFAULT 'unpaid',
  paid_amount DECIMAL(12,2) DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

ALTER TABLE patients
  ADD CONSTRAINT fk_patients_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL,
  ADD CONSTRAINT fk_patients_room FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE SET NULL;
INSERT INTO users (username, password_hash, role, full_name)
VALUES
 ('admin', SHA2('12345', 256), 'admin', 'System Administrator');