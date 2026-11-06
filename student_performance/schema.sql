CREATE DATABASE IF NOT EXISTS student_performance;
USE student_performance;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no    VARCHAR(20)  NOT NULL UNIQUE,
    name       VARCHAR(100) NOT NULL,
    section    VARCHAR(10)  NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id   INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL UNIQUE,
    max_marks    DECIMAL(6,2) NOT NULL,
    pass_marks   DECIMAL(6,2) NOT NULL,
    CONSTRAINT chk_max  CHECK (max_marks > 0),
    CONSTRAINT chk_pass CHECK (pass_marks >= 0 AND pass_marks <= max_marks)
);

CREATE TABLE IF NOT EXISTS marks (
    mark_id        INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT          NOT NULL,
    subject_id     INT          NOT NULL,
    assessment     VARCHAR(50)  NOT NULL,
    marks_obtained DECIMAL(6,2) NOT NULL,
    CONSTRAINT chk_marks CHECK (marks_obtained >= 0),
    CONSTRAINT uq_mark UNIQUE (student_id, subject_id, assessment),
    CONSTRAINT fk_marks_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_marks_subject FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);
