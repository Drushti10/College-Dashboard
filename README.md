# MIT Academy of Engineering — Smart Academic Management Portal

A modern, enterprise-grade **Smart Academic Management Portal** designed for autonomous engineering institutions. Built with **Node.js, Express, EJS, and express-session**, featuring persistent JSON data storage, authentic campus photography, intelligent student tools, and a powerful Faculty Command Center.

---

## 🏛 Quick Start Instructions

You can open and run this project immediately in **Visual Studio Code**:

```bash
# 1. Install dependencies
npm install

# 2. Launch the server
node app.js
```

Then open your browser and navigate to:
👉 **[http://localhost:3000/login](http://localhost:3000/login)**

---

## 🔑 Pre-Configured Demo Credentials

The login page provides **1-Click Quick Demo Login** buttons, or you can enter credentials manually:

| Role | Institutional Email | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Student** | `student@college.com` | `123456` | Student Dashboard, Academic Health Score, What-If Simulator, Study Plan, Assignments, Timetable, Notices |
| **Faculty** | `teacher@college.com` | `teacher123` | Faculty Command Center, Performance Intelligence Analytics, At-Risk Student Detection, 360° Profiles, Question Generator, Full CRUD |

---

## 🌟 Key System Features

### 🎓 Student Experience & Innovation Tools
1. **Personalized Study Planner ("My Study Plan")**:
   - Structured weekly study slots tailored to core subjects (DSA, DBMS, ML, CN, DAA, SE).
   - Highlights exam focus areas, coding practice, and revision routines.
2. **Academic Health / Performance Score**:
   - Multi-metric composite diagnostic index (0–100) combining Attendance (30%), Marks (40%), Assignment Delivery (20%), and Study Consistency (10%).
   - Displays clear qualitative health classification (*Excellent*, *Good*, or *Needs Attention*).
3. **Interactive What-If Grade & Attendance Simulator**:
   - Live client-side simulation tool.
   - **Attendance Forecast**: Test *"What will my attendance become if I attend the next N classes?"* with real-time percentage change.
   - **Grade Forecast**: Project revised course average based on target score in upcoming internal assessments.
4. **Deadline Priority & Smart Task Management**:
   - Tasks categorized by urgency: **Urgent** (Due within 48h), **Upcoming** (Due in 3–5 days), **Later**, and **Completed**.
   - Direct 1-click submission workflow with status feedback.
5. **Career Readiness & Skill Progress**:
   - Proficiency meters and milestones across Python, SQL, DSA, Machine Learning, and Technical Communication.
6. **Campus Photography & Student Life Showcase**:
   - Authentic college photographs highlighting the Central Library, High-Performance Computing Labs, Robotics Innovation Hub, and Symposium Halls.

---

### 👨‍🏫 Faculty Command Center & Intelligence
1. **Class Performance Intelligence (`/teacher/analytics`)**:
   - Real-time KPI summaries: Total Enrolled, Class Mean CGPA, Average Attendance, Pass Percentage.
   - Interactive Chart.js visualizations for Subject Performance Comparisons and CGPA Distribution.
   - Dean's Merit Honor Roll and statutory attendance compliance brackets.
2. **At-Risk Student Early Warning Detection (`/teacher/at-risk`)**:
   - Multi-factor automated deficiency identification (Attendance < 75%, Marks < 60%, CGPA < 6.0).
   - Risk categorization: **HIGH RISK**, **MEDIUM RISK**, and **LOW RISK**.
   - Clear institutional disclaimer stating this is an academic performance indicator.
   - Direct triggers to inspect student dossier and log counseling notes.
3. **Student 360° Academic Performance Dossier (`/teacher/students/:id/profile`)**:
   - Complete academic dossier with bio, contact details, attendance gauge, subject-wise marks charts, and chronological counseling history.
4. **Faculty Intervention & Mentoring Registry (`/teacher/interventions`)**:
   - Full CRUD to log 1-on-1 counseling: Student Name, Roll No, Issue Observed, Mentoring Action Taken, Follow-up Date, and Status (Pending / Resolved).
5. **Curriculum Question Paper Generator (`/teacher/question-generator`)**:
   - Syllabus-aware assessment engine with built-in curriculum question bank for core engineering disciplines.
   - Configurable: Subject, Topic, Bloom's Difficulty, Number of Questions, Total Marks.
   - Outputs print-ready examination layout with institutional header, instructions, Section A/B divisions, and marks breakdown.
6. **Smart Notice Creator (`/teacher/notices`)**:
   - Live drafting tool with real-time preview reflecting exactly how notices appear on student feeds.
   - Priority tagging (**Normal**, **Important**, **Urgent**) and category filters (**Academic**, **Event**, **Examination**, **Placement**, **Library**).
7. **Complete Faculty CRUD Suite**:
   - **Students CRUD**: Create, Read (with search), Update (modal), Delete (with confirmation).
   - **Marks CRUD**: Record, filter, update scores, and delete marks.
   - **Attendance CRUD**: Log lecture participation, inspect compliance badges, edit, and delete.
   - **Assignments CRUD**: Publish problem sets, set deadlines, and manage lifecycle.
   - **Notices CRUD**: Broadcast campus announcements and manage broadcasts.

---

## 📁 Project Architecture

```
student-dashboard-complete/
├── app.js                    # Express application server, routing, and intelligence logic
├── package.json              # Project metadata and dependencies (ejs, express, express-session)
├── README.md                 # Complete documentation and user guide
│
├── data/                     # Persistent JSON database
│   ├── users.json            # Authentication credentials & role profiles
│   ├── students.json         # Enrolled student identities, CGPA, attendance
│   ├── marks.json            # Subject-wise continuous evaluation marks
│   ├── attendance.json       # Course lecture & practical attendance percentages
│   ├── assignments.json      # Coursework deliverables, deadlines, and status
│   ├── notices.json          # Prioritized bulletins and announcements
│   ├── interventions.json    # Faculty counseling and mentoring logs
│   ├── study_plans.json      # Weekly personalized study routines
│   └── skills.json           # Career competencies and readiness progress
│
├── public/                   # Static web assets
│   ├── css/
│   │   └── style.css         # Academic enterprise design system & responsive styling
│   ├── js/
│   │   └── script.js         # Client-side calculators, search filters, and modals
│   └── images/               # High-quality campus photography
│       ├── login-bg.jpg      # Institutional campus facade for login
│       ├── mit-campus.jpg    # MIT Academy campus grounds
│       ├── campus-life.jpg   # Campus student life
│       ├── library.jpg       # Central library & study commons
│       ├── lab-computer.jpg  # Data Science & computing lab
│       ├── robotics-lab.jpg  # Robotics & IoT workshop
│       ├── seminar.jpg       # Auditorium & symposium hall
│       ├── sports-campus.jpg # Sports complex & athletics
│       ├── campus-collab.jpg # Student collaboration & hackathons
│       └── faculty-mentoring.jpg # Faculty-student academic interaction
│
└── views/                    # EJS Templates
    ├── 403.ejs               # Role authorization error page
    ├── 404.ejs               # Page not found error page
    ├── login.ejs             # Institutional portal login page
    ├── partials/
    │   ├── student-header.ejs # Student top navigation bar
    │   ├── student-nav.ejs    # Student sidebar navigation
    │   ├── teacher-header.ejs # Faculty top navigation bar
    │   └── teacher-nav.ejs    # Faculty sidebar navigation
    ├── student/
    │   ├── dashboard.ejs      # Unified student intelligence dashboard
    │   ├── profile.ejs        # Student academic dossier
    │   ├── attendance.ejs     # Attendance compliance & forecast tool
    │   ├── marks.ejs          # Subject evaluations & score simulator
    │   ├── assignments.ejs    # Priority-tiered smart task tracker
    │   ├── timetable.ejs      # Weekly lecture & lab timetable
    │   └── notices.ejs        # Campus bulletins & event highlights
    └── teacher/
        ├── dashboard.ejs      # Faculty Command Center
        ├── analytics.ejs      # Class Performance Intelligence
        ├── at-risk.ejs        # Early Warning Detection
        ├── student-profile.ejs # Student 360° Academic Dossier
        ├── question-generator.ejs # AI Question Paper Generator
        ├── interventions.ejs  # Mentoring & Intervention Logs
        ├── students.ejs       # Students CRUD Management
        ├── marks.ejs          # Marks & Assessment CRUD
        ├── attendance.ejs     # Attendance CRUD Roster
        ├── assignments.ejs    # Coursework CRUD Administration
        └── notices.ejs        # Smart Notice Publisher
```

---

## 🔒 Security & Role Authorization

- Session authentication backed by `express-session`.
- Strict route guards (`studentOnly` and `teacherOnly` middleware):
  - Students cannot access `/teacher` routes (returns `403 Forbidden`).
  - Faculty cannot access `/dashboard` routes (returns `403 Forbidden`).
  - Unauthenticated requests to protected endpoints redirect to `/login`.
- Form validations, deletion confirmation dialogs, and safe JSON fallback handling to prevent application crashes.

---

© 2026 MIT Academy of Engineering, Pune. All rights reserved.
