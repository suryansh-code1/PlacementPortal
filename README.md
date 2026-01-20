---
title: Placement Portal
emoji: 🎓
colorFrom: blue
colorTo: purple
sdk: docker
app_file: main.py
pinned: false
---

# 🎓 Placement Portal

A comprehensive web application for managing campus placement activities, connecting students with companies, and streamlining the recruitment process.

## 📋 Overview

The Placement Portal is a Flask-based web application designed to facilitate campus recruitment by providing a centralized platform for:
- **Students** to browse and apply for placement drives
- **Companies** to create and manage placement drives
- **Administrators** to oversee the entire placement process

## ✨ Features

### 👨‍💼 Admin Features
- Dashboard with key statistics (students, companies, applications, drives)
- Approve/reject company registrations
- Approve/reject placement drives
- Manage students and companies (view, delete, blacklist, activate)
- Search functionality for students and companies

### 🏢 Company Features
- Company registration with approval workflow
- Create and manage placement drives
- View and manage applicants
- Update application status (shortlisted, selected, rejected)
- Edit and close drives

### 👨‍🎓 Student Features
- Student registration and profile management
- Browse approved placement drives
- Apply for placement drives
- View application history and status
- Update profile information

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, Bootstrap
- **Password Security**: Werkzeug password hashing

## 📁 Project Structure

```
PLACEMENT PORTAL/
├── main.py                    # Application entry point
├── instance/                  # SQLite database storage
│   └── placement.db
└── application/
    ├── __init__.py           # Flask app factory
    ├── models.py             # Database models
    ├── controllers.py        # Routes and business logic
    ├── static/               # Static assets (CSS, JS)
    └── templates/            # HTML templates
        ├── base.html         # Base template
        ├── login.html        # Login page
        ├── register.html     # Registration selection
        ├── register_company.html
        ├── register_student.html
        ├── admin/           # Admin templates
        ├── company/         # Company templates
        └── student/         # Student templates
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   cd "PLACEMENT PORTAL"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-login werkzeug
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   
   Open your browser and navigate to: `http://127.0.0.1:5000`

## 🔐 Default Admin Credentials

On first run, an admin account is automatically created:

| Email | Password |
|-------|----------|
| `admin@portal.com` | `admin123` |

> ⚠️ **Security Note**: Change the default admin password immediately in a production environment.

## 📊 Database Models

### User
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| email | String | Unique email address |
| password_hash | String | Hashed password |
| role | String | `admin`, `company`, or `student` |
| is_active | Boolean | Account status |
| created_at | DateTime | Registration timestamp |

### CompanyProfile
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User |
| name | String | Company name |
| hr_contact | String | HR contact information |
| website | String | Company website |
| approval_status | String | `pending`, `approved`, `rejected` |

### StudentProfile
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User |
| name | String | Student name |
| student_id | String | Unique student ID |
| contact | String | Contact number |
| resume_bio | Text | Resume/Bio information |

### PlacementDrive
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| company_id | Integer | Foreign key to CompanyProfile |
| title | String | Drive title |
| description | Text | Job description |
| eligibility | Text | Eligibility criteria |
| deadline | DateTime | Application deadline |
| status | String | `pending`, `approved`, `rejected`, `closed` |

### Application
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| student_id | Integer | Foreign key to StudentProfile |
| drive_id | Integer | Foreign key to PlacementDrive |
| status | String | `applied`, `shortlisted`, `selected`, `rejected` |
| applied_date | DateTime | Application timestamp |

## 🔒 Role-Based Access Control

The application implements role-based access control:

- **Public Routes**: Login, Registration
- **Admin Routes** (`/admin/*`): Dashboard, company/student management, approvals
- **Company Routes** (`/company/*`): Dashboard, drive management, applicant management
- **Student Routes** (`/student/*`): Dashboard, profile, browse drives, apply

## 📝 Workflow

### Company Registration Flow
1. Company registers with details
2. Admin reviews and approves/rejects
3. Approved companies can create drives

### Placement Drive Flow
1. Company creates a placement drive
2. Admin approves the drive
3. Students can view and apply
4. Company reviews applications and updates status

### Student Application Flow
1. Student registers and completes profile
2. Browse approved placement drives
3. Apply for eligible drives
4. Track application status in history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open-source and available for educational purposes.

## 📧 Support

For any queries or issues, please open an issue in the repository.

---

**Built with ❤️ for Campus Placements**
