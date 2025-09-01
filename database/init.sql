-- database/init.sql
CREATE DATABASE IF NOT EXISTS african_lms;
USE african_lms;

-- Users table with different roles
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student',
    phone_number VARCHAR(20),
    country VARCHAR(50),
    language_preference VARCHAR(10) DEFAULT 'en',
    is_teacher_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Resources table for learning materials
CREATE TABLE resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(255),
    file_type ENUM('pdf', 'video', 'text', 'slides', 'link') NOT NULL,
    subject VARCHAR(100) NOT NULL,
    grade_level VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    tags TEXT,
    uploaded_by INT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN DEFAULT FALSE,
    view_count INT DEFAULT 0,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Translations table
CREATE TABLE translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    language VARCHAR(10) NOT NULL,
    translated_title VARCHAR(255),
    translated_description TEXT,
    translated_content TEXT, -- For text resources
    translation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

-- Ratings table
CREATE TABLE ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, resource_id)
);

-- Text-to-speech cache table
CREATE TABLE text_to_speech (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    language VARCHAR(10) NOT NULL,
    audio_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

-- Summaries table
CREATE TABLE summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    language VARCHAR(10) NOT NULL,
    summary_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

-- USSD sessions table
CREATE TABLE ussd_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    menu_level VARCHAR(50) DEFAULT 'main',
    selected_subject VARCHAR(100),
    selected_grade VARCHAR(50),
    selected_resource_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert initial admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role, is_teacher_verified) 
VALUES ('admin', 'admin@africanlms.org', '$2b$12$Wz5lUZ5q5q5q5q5q5q5q5u5q5q5q5q5q5q5q5q5q5q5q5q5q5q5q', 'admin', TRUE);