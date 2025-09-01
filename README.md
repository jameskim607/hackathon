# African LMS - Learning Management System

A comprehensive learning management system designed for African contexts, featuring USSD access for low-connectivity areas.

## Features

- **USSD Access**: Access learning materials without internet
- **Multi-language Support**: Resources available in multiple African languages
- **AI-powered Features**: Automatic translation, summarization, and text-to-speech
- **Teacher Portal**: Upload and manage educational resources
- **Student Portal**: Browse and access learning materials
- **Offline Support**: Progressive Web App functionality

## Installation

### Prerequisites

- Python 3.8+
- MySQL 5.7+
- Node.js (for frontend serving)

### Backend Setup

1. Create a MySQL database named `african_lms`
2. Update the database connection string in `backend/app/database.py`
3. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt