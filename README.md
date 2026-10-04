# CampusHub — College Club Event Management System

A full-stack web application for managing college clubs and campus events, built with Python (Flask), SQLite, and Vanilla HTML/CSS/JS.

---

## 🚀 Features

### Student
- Browse and search all approved clubs
- Join and leave clubs
- Register and unregister for events
- Personalized dashboard with activity overview
- Community discussion board participation

### Club Admin
- Create and manage club profile
- Add, edit, and delete events
- View registered participants list
- Manage club members
- Moderate discussion board (pin, lock, delete)

### Super Admin
- Approve and reject club registrations
- Manage all users, clubs, and events
- Real-time analytics dashboard with Chart.js
- Platform-wide overview and statistics

---

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | HTML5, CSS3, JavaScript, Jinja2     |
| Backend    | Python 3.8+, Flask 3.0+             |
| Database   | SQLite                              |
| Security   | PBKDF2-SHA256, Flask Sessions       |
| Charts     | Chart.js 4.x                        |
| Fonts      | Google Fonts (Playfair, DM Sans)    |

---

## 📁 Project Structure

```
campushub/
│
├── app.py                  ← Main Flask application
├── schema.sql              ← Database schema and table definitions
├── requirements.txt        ← Python dependencies
│
├── instance/
│   └── campushub.db        ← SQLite database (auto-created)
│
├── static/
│   ├── css/
│   │   └── main.css        ← Main stylesheet with dark mode
│   └── js/
│       └── main.js         ← Client-side JavaScript
│
└── templates/
    ├── base.html                  ← Base layout with navbar
    ├── home.html                  ← Landing page
    ├── auth.html                  ← Login and Register page
    ├── clubs.html                 ← Clubs listing page
    ├── club_detail.html           ← Club detail page
    ├── events.html                ← Events listing page
    ├── event_detail.html          ← Event detail page
    ├── dashboard_student.html     ← Student dashboard
    ├── dashboard_club_admin.html  ← Club admin dashboard
    ├── dashboard_admin.html       ← Super admin dashboard
    ├── analytics.html             ← Analytics dashboard
    ├── discussion_board.html      ← Club discussion board
    ├── thread_detail.html         ← Thread detail with replies
    ├── thread_form.html           ← New thread form
    ├── event_form.html            ← Create and edit event form
    ├── club_form.html             ← Create and edit club form
    └── error.html                 ← 404 and 500 error pages
```

---

## ⚙️ Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1 — Clone the Repository
```bash
git clone https://github.com/yourusername/campushub.git
cd campushub
```

### Step 2 — Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the Application
```bash
python app.py
```

### Step 5 — Open in Browser
```
http://localhost:5000
```

The database is **automatically created and seeded** on first run.
No manual setup required.

---

## 🔑 Demo Accounts

| Role        | Email                  | Password   |
|-------------|------------------------|------------|
| Super Admin | admin@campus.edu       | Admin@123  |
| Club Admin  | sarah@campus.edu       | Pass@123   |
| Club Admin  | marcus@campus.edu      | Pass@123   |
| Student     | alex@campus.edu        | Pass@123   |
| Student     | priya@campus.edu       | Pass@123   |
| Student     | jake@campus.edu        | Pass@123   |

---

## 🗃️ Database Schema

### Tables
- **users** — Stores all user accounts with hashed passwords and roles
- **clubs** — Stores club profiles with approval status
- **events** — Stores events with date, venue, and capacity
- **registrations** — Maps students to registered events
- **club_members** — Maps students to joined clubs
- **discussion_threads** — Stores club discussion board threads
- **discussion_replies** — Stores replies to discussion threads
- **thread_likes** — Stores user likes on discussion threads

---

## 📡 API Routes

### Authentication
| Method | Route         | Description        |
|--------|---------------|--------------------|
| GET    | /login        | Login page         |
| POST   | /login        | Process login      |
| GET    | /register     | Register page      |
| POST   | /register     | Process register   |
| GET    | /logout       | Logout user        |

### Clubs
| Method | Route                      | Description            |
|--------|----------------------------|------------------------|
| GET    | /clubs                     | List all clubs         |
| GET    | /clubs/<id>                | Club detail page       |
| POST   | /clubs/join/<id>           | Join a club            |
| POST   | /clubs/leave/<id>          | Leave a club           |
| GET    | /manage/club/create        | Create club form       |
| POST   | /manage/club/create        | Submit new club        |
| GET    | /manage/club/edit          | Edit club form         |
| POST   | /manage/club/edit          | Save club changes      |

### Events
| Method | Route                         | Description              |
|--------|-------------------------------|--------------------------|
| GET    | /events                       | List all events          |
| GET    | /events/<id>                  | Event detail page        |
| POST   | /events/register/<id>         | Register for event       |
| POST   | /events/unregister/<id>       | Unregister from event    |
| GET    | /manage/events/create         | Create event form        |
| POST   | /manage/events/create         | Submit new event         |
| GET    | /manage/events/edit/<id>      | Edit event form          |
| POST   | /manage/events/edit/<id>      | Save event changes       |
| POST   | /manage/events/delete/<id>    | Delete event             |

### Discussion Board
| Method | Route                                  | Description           |
|--------|----------------------------------------|-----------------------|
| GET    | /clubs/<id>/discuss                    | Discussion board      |
| GET    | /clubs/<id>/discuss/new                | New thread form       |
| POST   | /clubs/<id>/discuss/new                | Submit new thread     |
| GET    | /clubs/<id>/discuss/<thread_id>        | Thread detail         |
| POST   | /clubs/<id>/discuss/<thread_id>        | Post reply            |
| POST   | /discuss/like/<thread_id>              | Like or unlike thread |
| POST   | /discuss/pin/<thread_id>               | Pin or unpin thread   |
| POST   | /discuss/lock/<thread_id>              | Lock or unlock thread |
| POST   | /discuss/delete/thread/<thread_id>     | Delete thread         |
| POST   | /discuss/delete/reply/<reply_id>       | Delete reply          |

### Admin
| Method | Route                              | Description            |
|--------|------------------------------------|------------------------|
| GET    | /dashboard                         | Role-based dashboard   |
| GET    | /analytics                         | Analytics dashboard    |
| POST   | /admin/clubs/<action>/<id>         | Approve, reject, delete|
| POST   | /admin/users/deactivate/<id>       | Deactivate user        |
| POST   | /manage/members/remove/<id>        | Remove club member     |
| POST   | /toggle-theme                      | Toggle dark mode       |

---

## 🔐 Security Features

- PBKDF2-SHA256 password hashing using Werkzeug
- Session-based authentication with Flask
- Role-based access control using custom decorators
- Parameterized SQL queries preventing injection attacks
- Server-side input validation on all forms
- Route protection for admin and club admin pages

---

## 🌙 Additional Features

- Dark mode toggle persisted through user sessions
- Responsive design for desktop and mobile
- Real-time registration capacity tracking
- Automatic event status tracking
- Community discussion board with threading
- AJAX-powered like button without page reload
- Live search filtering on admin user table
- Toast notifications for all user actions
- Countdown timer on upcoming event pages
- Category filters and keyword search on listings

---

## 🚀 Deployment

### PythonAnywhere (Free)
1. Upload project files to PythonAnywhere
2. Create virtual environment and install requirements
3. Configure WSGI file to point to app.py
4. Set SECRET_KEY in environment variables
5. Reload the web app

### Render
1. Push code to GitHub repository
2. Connect repository to Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add SECRET_KEY environment variable

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
PORT=5000
```

---

## 📦 Requirements

```
flask>=3.0.0
werkzeug>=3.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 👨‍💻 Author

**Durga**

## 🙏 Acknowledgements

- Flask Documentation — https://flask.palletsprojects.com
- Chart.js Documentation — https://www.chartjs.org
- SQLite Documentation — https://www.sqlite.org
- Werkzeug Documentation — https://werkzeug.palletsprojects.com
- Google Fonts — https://fonts.google.com
- OWASP Security Guidelines — https://owasp.org
