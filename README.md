# FitSync

> A full-stack gym management web application built with **FastAPI**, **Jinja2**, **Python**, and **MySQL** for managing members, classes, attendance, equipment, and maintenance workflows.

## About

FitSync is a database-driven gym management platform designed to simulate gym operations. It provides dedicated interfaces for both members and employees, enabling streamlined management of memberships, class registrations, check-ins, equipment maintenance, and administrative tasks.

Developed as part of **CSI 3450: Database Design & Implementation** at **Oakland University**, this project demonstrates practical full-stack development combined with relational database design principles.

---

## Features

### Member Portal
- View and update profile information
- Manage emergency contact information
- Browse and register for available classes
- Record and view check-in history

### Employee Portal
- Manage gym members
- Add, edit, and delete member accounts
- Manage class offerings
- Track class attendance
- Record and view member check-ins
- Manage equipment inventory
- Create and manage maintenance tickets

---

## Tech Stack

- **Backend:** Python, FastAPI  
- **Frontend:** HTML, CSS, Jinja2  
- **Database:** MySQL  
- **Database Connector:** mysql-connector-python  
- **Environment Management:** python-dotenv  
- **Server:** Uvicorn  

---

## Project Structure

```bash
CSI-3450-FitSync/
├── app/
│   ├── main.py
│   └── database/
│       └── setup.py
├── static/
│   ├── styles.css
│   └── logo.png
├── templates/
│   ├── login.html
│   ├── member_profile.html
│   ├── member_classes.html
│   ├── member_checkins.html
│   ├── employee_attendance.html
│   ├── employee_checkins.html
│   ├── employee_edit_class.html
│   ├── employee_edit_member.html
│   ├── employee_new_class.html
│   ├── employee_new_member.html
│   ├── employee_tickets.html
│   ├── employee_equipment.html
│   └── employee_member.html
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```
---

## Installation & Setup

### Clone Repository

```bash
git clone https://github.com/wbenedetto/CSI-3450-FitSync.git  
cd CSI-3450-FitSync
```
### Create Virtual Environment

```bash
python -m venv venv  
```
**Windows:**  
```bash
venv\Scripts\activate  
```
**Mac / Linux:**
```bash 
source venv/bin/activate  
```
### Install Dependencies
```bash
pip install -r requirements.txt  
```
### Configure Environment Variables

Create a `.env` file in the root directory:
```bash
DB_HOST=localhost  
DB_USER=root  
DB_PASS=yourpassword  
DB_NAME=fitsync  
```

### Initialize Database
```bash
python app/database/setup.py  
```
### Run Development Server
```bash
uvicorn app.main:app --reload  
```
Application will be available at: http://127.0.0.1:8000  

---

## Usage

### Sample Login IDs

**Member ID:** 4001  
**Employee ID:** 2001  

---

## Database Architecture

FitSync uses a normalized relational database consisting of the following entities:

- Member  
- Employee  
- Tier  
- EContact
- Class  
- Registration  
- CheckIn  
- Equipment  
- Ticket  

---

## Key Concepts Demonstrated

- Relational Database Design  
- ERD / Normalization  
- CRUD Operations  
- FastAPI Backend Development  
- Server-Side Templating  
- Connection Pooling  
- Full-Stack Application Architecture  

---

## Contributors

<a href="https://github.com/wbenedetto/CSI-3450-FitSynce/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=wbenedetto/CSI-3450-FitSync" alt="contrib.rocks image" />
</a>

---

## License

This project is intended for educational purposes.
