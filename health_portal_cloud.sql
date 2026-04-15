-- ==============================================================
--   HEALTH PORTAL — COMPLETE CLOUD MySQL SQL SCRIPT
--   Database  : health_portal_db
--   Engine    : MySQL 8.x  (compatible with PlanetScale / AWS RDS / GCP Cloud SQL)
--   Generated : 2026-04-15
-- ==============================================================

-- ─────────────────────────────────────────────
--  STEP 1 : CREATE & USE DATABASE
-- ─────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS health_portal_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE health_portal_db;

-- ─────────────────────────────────────────────
--  STEP 2 : CREATE TABLES
--  (FK-safe order: independent tables first)
-- ─────────────────────────────────────────────

-- 2.1  USERS  (Django custom AbstractUser → accounts.User)
CREATE TABLE IF NOT EXISTS `users` (
    `id`                    BIGINT          NOT NULL AUTO_INCREMENT,
    `password`              VARCHAR(128)    NOT NULL,
    `last_login`            DATETIME(6)     NULL,
    `is_superuser`          TINYINT(1)      NOT NULL DEFAULT 0,
    `username`              VARCHAR(150)    NOT NULL,
    `first_name`            VARCHAR(150)    NOT NULL DEFAULT '',
    `last_name`             VARCHAR(150)    NOT NULL DEFAULT '',
    `is_staff`              TINYINT(1)      NOT NULL DEFAULT 0,
    `is_active`             TINYINT(1)      NOT NULL DEFAULT 1,
    `date_joined`           DATETIME(6)     NOT NULL,
    -- Custom fields
    `role`                  VARCHAR(20)     NOT NULL DEFAULT 'PATIENT'
                            COMMENT 'PATIENT | DOCTOR | HOSPITAL_ADMIN | SYSTEM_ADMIN',
    `email`                 VARCHAR(254)    NOT NULL,
    `phone`                 VARCHAR(15)     NULL,
    `date_of_birth`         DATE            NULL,
    `address`               LONGTEXT        NULL,
    `profile_picture`       VARCHAR(100)    NULL,
    `email_verified`        TINYINT(1)      NOT NULL DEFAULT 0,
    `verification_token`    VARCHAR(100)    NULL,
    `is_approved`           TINYINT(1)      NOT NULL DEFAULT 1,
    `created_at`            DATETIME(6)     NOT NULL,
    `updated_at`            DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_users_username`  (`username`),
    UNIQUE KEY `uq_users_email`     (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.2  HOSPITALS
CREATE TABLE IF NOT EXISTS `hospitals` (
    `id`                    BIGINT          NOT NULL AUTO_INCREMENT,
    `name`                  VARCHAR(200)    NOT NULL,
    `registration_number`   VARCHAR(50)     NOT NULL,
    `email`                 VARCHAR(254)    NOT NULL,
    `phone`                 VARCHAR(15)     NOT NULL,
    `address_line1`         VARCHAR(200)    NOT NULL,
    `address_line2`         VARCHAR(200)    NULL,
    `city`                  VARCHAR(100)    NOT NULL,
    `state`                 VARCHAR(100)    NOT NULL,
    `pincode`               VARCHAR(10)     NOT NULL,
    `country`               VARCHAR(100)    NOT NULL DEFAULT 'India',
    `description`           LONGTEXT        NULL,
    `facilities`            LONGTEXT        NULL,
    `specializations`       LONGTEXT        NULL,
    `admin_id`              BIGINT          NULL,
    `is_verified`           TINYINT(1)      NOT NULL DEFAULT 0,
    `is_active`             TINYINT(1)      NOT NULL DEFAULT 1,
    `logo`                  VARCHAR(100)    NULL,
    `rating`                DECIMAL(3,2)    NOT NULL DEFAULT 0.00,
    `created_at`            DATETIME(6)     NOT NULL,
    `updated_at`            DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_hospitals_reg_no` (`registration_number`),
    CONSTRAINT `fk_hospitals_admin`
        FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.3  DOCTOR PROFILES
CREATE TABLE IF NOT EXISTS `doctor_profiles` (
    `id`                        BIGINT          NOT NULL AUTO_INCREMENT,
    `user_id`                   BIGINT          NOT NULL,
    `specialization`            VARCHAR(100)    NOT NULL,
    `qualifications`            LONGTEXT        NOT NULL,
    `license_number`            VARCHAR(50)     NOT NULL,
    `experience_years`          INT             NOT NULL DEFAULT 0,
    `consultation_fee`          DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    `consultation_duration`     INT             NOT NULL DEFAULT 30
                                COMMENT 'Duration in minutes',
    `bio`                       LONGTEXT        NULL,
    `rating`                    DECIMAL(3,2)    NOT NULL DEFAULT 0.00,
    `total_consultations`       INT             NOT NULL DEFAULT 0,
    `is_available`              TINYINT(1)      NOT NULL DEFAULT 1,
    `is_verified`               TINYINT(1)      NOT NULL DEFAULT 0,
    `created_at`                DATETIME(6)     NOT NULL,
    `updated_at`                DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_doctor_profiles_user`    (`user_id`),
    UNIQUE KEY `uq_doctor_license`          (`license_number`),
    CONSTRAINT `fk_doctor_profiles_user`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.4  DOCTOR ↔ HOSPITAL  (ManyToMany junction)
CREATE TABLE IF NOT EXISTS `doctor_profiles_hospitals` (
    `id`            BIGINT  NOT NULL AUTO_INCREMENT,
    `doctorprofile_id`  BIGINT  NOT NULL,
    `hospital_id`       BIGINT  NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_doctor_hospital` (`doctorprofile_id`, `hospital_id`),
    CONSTRAINT `fk_dph_doctor`
        FOREIGN KEY (`doctorprofile_id`) REFERENCES `doctor_profiles` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_dph_hospital`
        FOREIGN KEY (`hospital_id`) REFERENCES `hospitals` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.5  DOCTOR AVAILABILITY
CREATE TABLE IF NOT EXISTS `doctor_availability` (
    `id`            BIGINT      NOT NULL AUTO_INCREMENT,
    `doctor_id`     BIGINT      NOT NULL,
    `day`           VARCHAR(10) NOT NULL
                    COMMENT 'MONDAY | TUESDAY | WEDNESDAY | THURSDAY | FRIDAY | SATURDAY | SUNDAY',
    `start_time`    TIME        NOT NULL,
    `end_time`      TIME        NOT NULL,
    `is_available`  TINYINT(1)  NOT NULL DEFAULT 1,
    `created_at`    DATETIME(6) NOT NULL,
    `updated_at`    DATETIME(6) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_doctor_avail` (`doctor_id`, `day`, `start_time`),
    CONSTRAINT `fk_availability_doctor`
        FOREIGN KEY (`doctor_id`) REFERENCES `doctor_profiles` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.6  PATIENT PROFILES
CREATE TABLE IF NOT EXISTS `patient_profiles` (
    `id`                            BIGINT          NOT NULL AUTO_INCREMENT,
    `user_id`                       BIGINT          NOT NULL,
    `blood_group`                   VARCHAR(3)      NULL
                                    COMMENT 'A+ | A- | B+ | B- | AB+ | AB- | O+ | O-',
    `height`                        DECIMAL(5,2)    NULL  COMMENT 'cm',
    `weight`                        DECIMAL(5,2)    NULL  COMMENT 'kg',
    `allergies`                     LONGTEXT        NULL,
    `chronic_conditions`            LONGTEXT        NULL,
    `current_medications`           LONGTEXT        NULL,
    `emergency_contact_name`        VARCHAR(100)    NULL,
    `emergency_contact_phone`       VARCHAR(15)     NULL,
    `emergency_contact_relation`    VARCHAR(50)     NULL,
    `created_at`                    DATETIME(6)     NOT NULL,
    `updated_at`                    DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_patient_profiles_user` (`user_id`),
    CONSTRAINT `fk_patient_profiles_user`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.7  APPOINTMENTS
CREATE TABLE IF NOT EXISTS `appointments` (
    `id`                    BIGINT          NOT NULL AUTO_INCREMENT,
    `patient_id`            BIGINT          NOT NULL,
    `doctor_id`             BIGINT          NOT NULL,
    `appointment_date`      DATE            NOT NULL,
    `appointment_time`      TIME            NULL,
    `duration`              INT             NOT NULL DEFAULT 30 COMMENT 'minutes',
    `consultation_type`     VARCHAR(20)     NOT NULL DEFAULT 'CLINIC'
                            COMMENT 'VIDEO | AUDIO | CLINIC',
    `urgency_level`         VARCHAR(20)     NOT NULL DEFAULT 'ROUTINE'
                            COMMENT 'ROUTINE | URGENT | EMERGENCY',
    `attachment`            VARCHAR(100)    NULL,
    `status`                VARCHAR(20)     NOT NULL DEFAULT 'PENDING'
                            COMMENT 'PENDING | CONFIRMED | COMPLETED | CANCELLED | NO_SHOW',
    `reason`                LONGTEXT        NULL,
    `symptoms`              LONGTEXT        NULL,
    `doctor_notes`          LONGTEXT        NULL,
    `consultation_fee`      DECIMAL(10,2)   NOT NULL,
    `is_paid`               TINYINT(1)      NOT NULL DEFAULT 0,
    `created_at`            DATETIME(6)     NOT NULL,
    `updated_at`            DATETIME(6)     NOT NULL,
    `cancelled_at`          DATETIME(6)     NULL,
    `cancellation_reason`   LONGTEXT        NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_appointments_patient`
        FOREIGN KEY (`patient_id`) REFERENCES `patient_profiles` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_appointments_doctor`
        FOREIGN KEY (`doctor_id`) REFERENCES `doctor_profiles` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.8  CONSULTATIONS
CREATE TABLE IF NOT EXISTS `consultations` (
    `id`                    BIGINT          NOT NULL AUTO_INCREMENT,
    `appointment_id`        BIGINT          NOT NULL,
    `room_id`               VARCHAR(100)    NOT NULL,
    `start_time`            DATETIME(6)     NULL,
    `end_time`              DATETIME(6)     NULL,
    `status`                VARCHAR(20)     NOT NULL DEFAULT 'SCHEDULED'
                            COMMENT 'SCHEDULED | ACTIVE | IN_PROGRESS | COMPLETED | CANCELLED',
    `consultation_notes`    LONGTEXT        NULL,
    `diagnosis`             LONGTEXT        NULL,
    `recording_url`         VARCHAR(200)    NULL,
    `created_at`            DATETIME(6)     NOT NULL,
    `updated_at`            DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_consultations_appointment` (`appointment_id`),
    UNIQUE KEY `uq_consultations_room`        (`room_id`),
    CONSTRAINT `fk_consultations_appointment`
        FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.9  PRESCRIPTIONS
CREATE TABLE IF NOT EXISTS `prescriptions` (
    `id`                BIGINT          NOT NULL AUTO_INCREMENT,
    `appointment_id`    BIGINT          NULL,
    `consultation_id`   BIGINT          NULL,
    `patient_id`        BIGINT          NOT NULL,
    `doctor_id`         BIGINT          NOT NULL,
    `is_private`        TINYINT(1)      NOT NULL DEFAULT 0,
    `diagnosis`         LONGTEXT        NOT NULL,
    `symptoms`          LONGTEXT        NULL,
    `medications`       JSON            NOT NULL COMMENT '[{"name","dosage","frequency","duration"}]',
    `instructions`      LONGTEXT        NULL,
    `follow_up_date`    DATE            NULL,
    `lab_tests`         LONGTEXT        NULL,
    `doctor_signature`  VARCHAR(100)    NULL,
    `created_at`        DATETIME(6)     NOT NULL,
    `updated_at`        DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_prescriptions_appointment`
        FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_prescriptions_consultation`
        FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_prescriptions_patient`
        FOREIGN KEY (`patient_id`) REFERENCES `patient_profiles` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_prescriptions_doctor`
        FOREIGN KEY (`doctor_id`) REFERENCES `doctor_profiles` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.10  MEDICAL RECORDS
CREATE TABLE IF NOT EXISTS `medical_records` (
    `id`                BIGINT          NOT NULL AUTO_INCREMENT,
    `patient_id`        BIGINT          NOT NULL,
    `consultation_id`   BIGINT          NULL,
    `record_type`       VARCHAR(20)     NOT NULL
                        COMMENT 'PRESCRIPTION | LAB_REPORT | XRAY | MRI | CT_SCAN | OTHER',
    `title`             VARCHAR(200)    NOT NULL,
    `description`       LONGTEXT        NULL,
    `document`          VARCHAR(100)    NOT NULL,
    `uploaded_by_id`    BIGINT          NULL,
    `record_date`       DATE            NOT NULL,
    `created_at`        DATETIME(6)     NOT NULL,
    `updated_at`        DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_medical_records_patient`
        FOREIGN KEY (`patient_id`) REFERENCES `patient_profiles` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_medical_records_consultation`
        FOREIGN KEY (`consultation_id`) REFERENCES `consultations` (`id`)
        ON DELETE SET NULL,
    CONSTRAINT `fk_medical_records_uploaded_by`
        FOREIGN KEY (`uploaded_by_id`) REFERENCES `users` (`id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.11  PAYMENTS
CREATE TABLE IF NOT EXISTS `payments` (
    `id`                BIGINT          NOT NULL AUTO_INCREMENT,
    `appointment_id`    BIGINT          NOT NULL,
    `user_id`           BIGINT          NOT NULL,
    `amount`            DECIMAL(10,2)   NOT NULL,
    `payment_method`    VARCHAR(20)     NOT NULL DEFAULT 'PAYPAL'
                        COMMENT 'PAYPAL | STRIPE | CARD | UPI | WALLET',
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'PENDING'
                        COMMENT 'PENDING | COMPLETED | FAILED | REFUNDED',
    `transaction_id`    VARCHAR(200)    NULL,
    `paypal_order_id`   VARCHAR(200)    NULL,
    `description`       LONGTEXT        NULL,
    `created_at`        DATETIME(6)     NOT NULL,
    `updated_at`        DATETIME(6)     NOT NULL,
    `paid_at`           DATETIME(6)     NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_payments_transaction` (`transaction_id`),
    CONSTRAINT `fk_payments_appointment`
        FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_payments_user`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.12  REFUNDS
CREATE TABLE IF NOT EXISTS `refunds` (
    `id`                BIGINT          NOT NULL AUTO_INCREMENT,
    `payment_id`        BIGINT          NOT NULL,
    `amount`            DECIMAL(10,2)   NOT NULL,
    `reason`            LONGTEXT        NOT NULL,
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'REQUESTED'
                        COMMENT 'REQUESTED | APPROVED | REJECTED | COMPLETED',
    `admin_notes`       LONGTEXT        NULL,
    `processed_by_id`   BIGINT          NULL,
    `created_at`        DATETIME(6)     NOT NULL,
    `updated_at`        DATETIME(6)     NOT NULL,
    `completed_at`      DATETIME(6)     NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_refunds_payment`
        FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_refunds_processed_by`
        FOREIGN KEY (`processed_by_id`) REFERENCES `users` (`id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.13  SYSTEM ANALYTICS
CREATE TABLE IF NOT EXISTS `system_analytics` (
    `id`                        BIGINT          NOT NULL AUTO_INCREMENT,
    `date`                      DATE            NOT NULL,
    `total_users`               INT             NOT NULL DEFAULT 0,
    `new_users`                 INT             NOT NULL DEFAULT 0,
    `active_users`              INT             NOT NULL DEFAULT 0,
    `total_patients`            INT             NOT NULL DEFAULT 0,
    `total_doctors`             INT             NOT NULL DEFAULT 0,
    `total_appointments`        INT             NOT NULL DEFAULT 0,
    `completed_appointments`    INT             NOT NULL DEFAULT 0,
    `cancelled_appointments`    INT             NOT NULL DEFAULT 0,
    `total_consultations`       INT             NOT NULL DEFAULT 0,
    `completed_consultations`   INT             NOT NULL DEFAULT 0,
    `total_revenue`             DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    `total_payments`            INT             NOT NULL DEFAULT 0,
    `created_at`                DATETIME(6)     NOT NULL,
    `updated_at`                DATETIME(6)     NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_analytics_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2.14  ACTIVITY LOGS
CREATE TABLE IF NOT EXISTS `activity_logs` (
    `id`            BIGINT              NOT NULL AUTO_INCREMENT,
    `user_id`       BIGINT              NULL,
    `action`        VARCHAR(20)         NOT NULL
                    COMMENT 'LOGIN | LOGOUT | CREATE | UPDATE | DELETE | VIEW',
    `entity_type`   VARCHAR(50)         NULL,
    `entity_id`     INT                 NULL,
    `description`   LONGTEXT            NULL,
    `ip_address`    VARCHAR(39)         NULL,
    `user_agent`    LONGTEXT            NULL,
    `created_at`    DATETIME(6)         NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_activity_logs_user`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- ─────────────────────────────────────────────
--  STEP 3 : INSERT SAMPLE DATA
-- ─────────────────────────────────────────────

-- 3.1  USERS
--  Passwords below are bcrypt hashes for  "Password@123"
--  (In production Django hashes passwords automatically — never store plain text)
INSERT INTO `users`
    (password, is_superuser, username, first_name, last_name,
     is_staff, is_active, date_joined,
     role, email, phone, date_of_birth, is_approved,
     email_verified, created_at, updated_at)
VALUES
-- System Admin
('pbkdf2_sha256$600000$adminSalt$hashedpw==', 1, 'admin',
 'System', 'Admin', 1, 1, NOW(),
 'SYSTEM_ADMIN', 'admin@healthportal.com', '9000000001', '1985-01-15',
  1, 1, NOW(), NOW()),

-- Hospital Admin
('pbkdf2_sha256$600000$hospSalt$hashedpw==', 0, 'hosp_admin',
 'Ramesh', 'Kumar', 0, 1, NOW(),
 'HOSPITAL_ADMIN', 'ramesh.kumar@cityhospital.in', '9000000002', '1978-06-20',
  1, 1, NOW(), NOW()),

-- Doctor 1
('pbkdf2_sha256$600000$doc1Salt$hashedpw==', 0, 'dr_priya',
 'Priya', 'Sharma', 0, 1, NOW(),
 'DOCTOR', 'priya.sharma@healthportal.com', '9000000003', '1982-03-10',
  1, 1, NOW(), NOW()),

-- Doctor 2
('pbkdf2_sha256$600000$doc2Salt$hashedpw==', 0, 'dr_arjun',
 'Arjun', 'Mehta', 0, 1, NOW(),
 'DOCTOR', 'arjun.mehta@healthportal.com', '9000000004', '1979-11-05',
  1, 1, NOW(), NOW()),

-- Patient 1
('pbkdf2_sha256$600000$pat1Salt$hashedpw==', 0, 'patient_vijay',
 'Vijay', 'Anand', 0, 1, NOW(),
 'PATIENT', 'vijay.anand@gmail.com', '9000000005', '2002-07-14',
  1, 1, NOW(), NOW()),

-- Patient 2
('pbkdf2_sha256$600000$pat2Salt$hashedpw==', 0, 'patient_anitha',
 'Anitha', 'Raj', 0, 1, NOW(),
 'PATIENT', 'anitha.raj@gmail.com', '9000000006', '1995-04-22',
  1, 1, NOW(), NOW());


-- 3.2  HOSPITALS
INSERT INTO `hospitals`
    (name, registration_number, email, phone,
     address_line1, city, state, pincode, country,
     description, facilities, specializations,
     admin_id, is_verified, is_active, rating, created_at, updated_at)
VALUES
('City Multi-Specialty Hospital',
 'HOSP-TN-2021-001',
 'info@cityhospital.in', '044-12345678',
 '12, Anna Salai', 'Chennai', 'Tamil Nadu', '600002', 'India',
 'A leading multi-specialty hospital with state-of-the-art facilities.',
 'ICU, OT, Pharmacy, Lab, Radiology, Cafeteria',
 'Cardiology, Neurology, Orthopedics, Pediatrics, Dermatology',
 2, 1, 1, 4.50, NOW(), NOW()),

('Green Life Clinic',
 'HOSP-TN-2022-002',
 'contact@greenlifeclinic.in', '044-98765432',
 '45, Gandhi Road', 'Coimbatore', 'Tamil Nadu', '641001', 'India',
 'Affordable healthcare for all.',
 'OPD, Lab, Pharmacy',
 'General Medicine, Gynecology',
 NULL, 1, 1, 4.10, NOW(), NOW());


-- 3.3  DOCTOR PROFILES
INSERT INTO `doctor_profiles`
    (user_id, specialization, qualifications, license_number, experience_years,
     consultation_fee, consultation_duration, bio,
     rating, total_consultations, is_available, is_verified, created_at, updated_at)
VALUES
(3, 'Cardiology',
 'MBBS - SRMC Chennai, MD (Cardiology) - AIIMS Delhi, FACC',
 'TN-MED-2008-4521', 16,
 800.00, 30,
 'Dr. Priya Sharma is a senior cardiologist with 16 years of clinical experience.',
 4.70, 320, 1, 1, NOW(), NOW()),

(4, 'Neurology',
 'MBBS - KMC Manipal, DM (Neurology) - NIMHANS Bangalore',
 'TN-MED-2005-3310', 19,
 1000.00, 45,
 'Dr. Arjun Mehta specialises in stroke, epilepsy and movement disorders.',
 4.80, 480, 1, 1, NOW(), NOW());


-- 3.4  DOCTOR — HOSPITAL JUNCTION
INSERT INTO `doctor_profiles_hospitals` (doctorprofile_id, hospital_id)
VALUES
(1, 1),   -- Dr. Priya → City Hospital
(2, 1),   -- Dr. Arjun → City Hospital
(2, 2);   -- Dr. Arjun → Green Life Clinic


-- 3.5  DOCTOR AVAILABILITY
INSERT INTO `doctor_availability`
    (doctor_id, day, start_time, end_time, is_available, created_at, updated_at)
VALUES
-- Dr. Priya — Mon/Wed/Fri  09:00–13:00
(1, 'MONDAY',    '09:00:00', '13:00:00', 1, NOW(), NOW()),
(1, 'WEDNESDAY', '09:00:00', '13:00:00', 1, NOW(), NOW()),
(1, 'FRIDAY',    '09:00:00', '13:00:00', 1, NOW(), NOW()),
-- Dr. Arjun — Tue/Thu  10:00–16:00
(2, 'TUESDAY',   '10:00:00', '16:00:00', 1, NOW(), NOW()),
(2, 'THURSDAY',  '10:00:00', '16:00:00', 1, NOW(), NOW());


-- 3.6  PATIENT PROFILES
INSERT INTO `patient_profiles`
    (user_id, blood_group, height, weight,
     allergies, chronic_conditions, current_medications,
     emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
     created_at, updated_at)
VALUES
(5, 'B+', 172.50, 68.00,
 'Penicillin', 'None', 'None',
 'Anand Kumar', '9111111111', 'Father',
 NOW(), NOW()),

(6, 'O+', 158.00, 54.00,
 'Dust, Pollen', 'Asthma', 'Asthalin Inhaler',
 'Raj Suresh', '9222222222', 'Husband',
 NOW(), NOW());


-- 3.7  APPOINTMENTS
INSERT INTO `appointments`
    (patient_id, doctor_id, appointment_date, appointment_time, duration,
     consultation_type, urgency_level, status,
     reason, symptoms, consultation_fee, is_paid, created_at, updated_at)
VALUES
-- Vijay → Dr. Priya (Cardiology) — upcoming CONFIRMED
(1, 1, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '10:00:00', 30,
 'VIDEO', 'ROUTINE', 'CONFIRMED',
 'Routine cardiac check-up', 'Mild chest discomfort', 800.00, 1, NOW(), NOW()),

-- Anitha → Dr. Arjun (Neurology) — upcoming PENDING
(2, 2, DATE_ADD(CURDATE(), INTERVAL 7 DAY), '11:00:00', 45,
 'VIDEO', 'URGENT', 'PENDING',
 'Recurring headaches and dizziness', 'Severe headache, blurred vision', 1000.00, 0, NOW(), NOW()),

-- Vijay → Dr. Arjun — past COMPLETED
(1, 2, DATE_SUB(CURDATE(), INTERVAL 10 DAY), '10:00:00', 45,
 'CLINIC', 'ROUTINE', 'COMPLETED',
 'Follow-up for migraine', 'Occasional headache', 1000.00, 1, NOW(), NOW());


-- 3.8  CONSULTATIONS
INSERT INTO `consultations`
    (appointment_id, room_id, start_time, end_time,
     status, consultation_notes, diagnosis, created_at, updated_at)
VALUES
-- For appointment #1 (Vijay-Priya, upcoming)
(1, 'ROOM-2026-VJ-PRIYA-001', NULL, NULL,
 'SCHEDULED', NULL, NULL, NOW(), NOW()),

-- For appointment #3 (Vijay-Arjun, completed)
(3, 'ROOM-2026-VJ-ARJ-003',
 DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 10 DAY), '%Y-%m-%d 10:00:00'),
 DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 10 DAY), '%Y-%m-%d 10:45:00'),
 'COMPLETED',
 'Patient reports improvement. Continue current medication.',
 'Tension-type headache (G44.2)',
 NOW(), NOW());


-- 3.9  PRESCRIPTIONS
INSERT INTO `prescriptions`
    (appointment_id, consultation_id, patient_id, doctor_id,
     diagnosis, symptoms, medications, instructions, follow_up_date,
     is_private, created_at, updated_at)
VALUES
(3, 2, 1, 2,
 'Tension-type headache (G44.2)',
 'Occasional headache, mild nausea',
 '[{"name":"Tab. Sumatriptan 50mg","dosage":"50mg","frequency":"Once at onset of headache","duration":"As needed"},{"name":"Tab. Paracetamol 500mg","dosage":"500mg","frequency":"TID","duration":"5 days"}]',
 'Avoid screen exposure for long hours. Take adequate sleep. Hydrate well.',
 DATE_ADD(CURDATE(), INTERVAL 30 DAY),
 0, NOW(), NOW());


-- 3.10  PAYMENTS
INSERT INTO `payments`
    (appointment_id, user_id, amount, payment_method, status,
     transaction_id, description, created_at, updated_at, paid_at)
VALUES
-- Appointment #1 payment (Vijay-Priya, paid)
(1, 5, 800.00, 'STRIPE', 'COMPLETED',
 'pi_3OXtestStripe001', 'Video consultation with Dr. Priya Sharma',
 NOW(), NOW(), NOW()),

-- Appointment #3 payment (Vijay-Arjun, paid)
(3, 5, 1000.00, 'UPI', 'COMPLETED',
 'UPI-TXN-20260405-001', 'Clinic visit with Dr. Arjun Mehta',
 DATE_SUB(NOW(), INTERVAL 10 DAY),
 DATE_SUB(NOW(), INTERVAL 10 DAY),
 DATE_SUB(NOW(), INTERVAL 10 DAY));


-- 3.11  SYSTEM ANALYTICS  (today's snapshot)
INSERT INTO `system_analytics`
    (date, total_users, new_users, active_users, total_patients, total_doctors,
     total_appointments, completed_appointments, cancelled_appointments,
     total_consultations, completed_consultations,
     total_revenue, total_payments, created_at, updated_at)
VALUES
(CURDATE(), 6, 2, 4, 2, 2,
 3, 1, 0,
 2, 1,
 1800.00, 2, NOW(), NOW());


-- 3.12  ACTIVITY LOGS
INSERT INTO `activity_logs`
    (user_id, action, entity_type, entity_id, description, ip_address, created_at)
VALUES
(5, 'LOGIN',  NULL,          NULL, 'Patient Vijay logged in',             '127.0.0.1', NOW()),
(5, 'CREATE', 'Appointment', 1,    'Booked appointment #1 with Dr. Priya','127.0.0.1', NOW()),
(5, 'VIEW',   'Prescription',1,    'Viewed prescription #1',              '127.0.0.1', NOW()),
(3, 'LOGIN',  NULL,          NULL, 'Dr. Priya logged in',                 '127.0.0.1', NOW()),
(3, 'UPDATE', 'Appointment', 1,    'Confirmed appointment #1',            '127.0.0.1', NOW()),
(1, 'LOGIN',  NULL,          NULL, 'Admin logged in',                     '127.0.0.1', NOW());


-- ─────────────────────────────────────────────
--  END OF SCRIPT
-- ─────────────────────────────────────────────
