"""
CampusHub — College Club Event Management System
Flask Backend Application
"""

import os
import sqlite3
from datetime import datetime, date
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, g)
from werkzeug.security import generate_password_hash, check_password_hash

# ─── App Configuration ────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'campushub-dev-secret-change-in-production')
app.config['DATABASE'] = os.path.join(app.instance_path, 'campushub.db')
os.makedirs(app.instance_path, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
#  DATABASE LAYER
# ═══════════════════════════════════════════════════════════════════════════

def get_db():
    """Return a thread-local database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # rows behave like dicts
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables from schema.sql and seed demo data."""
    db = get_db()
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))
    db.commit()
    _seed_demo_data(db)


def _seed_demo_data(db):
    """Insert demo users, clubs, and events if DB is empty."""
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return  # already seeded

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today = date.today()

    # ── Users ──────────────────────────────────────────────────────────────
    users = [
        ('Super Admin',   'admin@campus.edu',       generate_password_hash('Admin@123'),   'super_admin'),
        ('Sarah Chen',    'sarah@campus.edu',        generate_password_hash('Pass@123'),    'club_admin'),
        ('Marcus Reed',   'marcus@campus.edu',       generate_password_hash('Pass@123'),    'club_admin'),
        ('Alex Johnson',  'alex@campus.edu',         generate_password_hash('Pass@123'),    'student'),
        ('Priya Patel',   'priya@campus.edu',        generate_password_hash('Pass@123'),    'student'),
        ('Jake Williams', 'jake@campus.edu',         generate_password_hash('Pass@123'),    'student'),
    ]
    db.executemany(
        "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?,?,?,?,?)",
        [(u[0], u[1], u[2], u[3], now) for u in users]
    )

    # ── Clubs ──────────────────────────────────────────────────────────────
    clubs = [
        ('Tech Innovators',     'Technology',   'Building the future through code, hardware, and innovation. We host hackathons, workshops, and guest lectures from industry leaders.',  2, 'approved'),
        ('Green Earth Society', 'Environment',  'Championing sustainability and environmental awareness. From tree planting to policy advocacy, we make the planet greener.',            3, 'approved'),
        ('Debate League',       'Academic',     'Sharpen your rhetoric and critical thinking. We compete nationally and train the next generation of public speakers.',                  2, 'approved'),
        ('Photography Circle',  'Arts',         'Capturing moments, telling stories through the lens. Regular photoshoots, exhibitions, and darkroom sessions.',                        2, 'pending'),
        ('Music Ensemble',      'Arts',         'Where rhythms meet melodies. Classical to contemporary, we celebrate all forms of music through performances and workshops.',           3, 'approved'),
    ]
    for c in clubs:
        db.execute(
            "INSERT INTO clubs (name, category, description, admin_id, status, created_at) VALUES (?,?,?,?,?,?)",
            (c[0], c[1], c[2], c[3], c[4], now)
        )

    # ── Events ─────────────────────────────────────────────────────────────
    events = [
        (1, 'Annual Hackathon 2025',            '48-hour coding marathon. Build innovative solutions. Prizes worth $10,000.',  '2025-08-15', '09:00', '2025-08-17', 'Engineering Block B, Hall 3', 200, 'upcoming',   'Technology'),
        (1, 'AI & Machine Learning Workshop',   'Hands-on workshop: ML fundamentals, neural networks, Python. Beginner friendly.', '2025-07-20', '14:00', '2025-07-20', 'CS Lab 101',               50,  'upcoming',   'Technology'),
        (3, 'National Debate Championship',     'Annual inter-college debate. Topics span climate policy to tech ethics.',     '2025-07-10', '10:00', '2025-07-12', 'Main Auditorium',            80,  'ongoing',    'Academic'),
        (2, 'Campus Sustainability Drive',      'Campus-wide cleanup and tree planting. Every participant gets a certificate.', '2025-06-30', '07:00', '2025-06-30', 'Campus Grounds',            150, 'completed',  'Environment'),
        (5, 'Spring Music Concert',             'Annual showcase of student musical talent. All genres welcome.',              '2025-08-05', '18:00', '2025-08-05', 'Open Air Theatre',           300, 'upcoming',   'Arts'),
    ]
    for e in events:
        db.execute(
            """INSERT INTO events (club_id, title, description, event_date, event_time,
               end_date, venue, max_participants, status, category, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (*e, now)
        )

    # ── Club Members ───────────────────────────────────────────────────────
    memberships = [(4,1),(4,3),(5,1),(5,2),(6,3)]
    db.executemany(
        "INSERT OR IGNORE INTO club_members (user_id, club_id, joined_at) VALUES (?,?,?)",
        [(m[0], m[1], now) for m in memberships]
    )

    # ── Event Registrations ────────────────────────────────────────────────
    regs = [(4,1),(5,1),(4,3),(6,3),(5,2)]
    db.executemany(
        "INSERT OR IGNORE INTO registrations (user_id, event_id, registered_at) VALUES (?,?,?)",
        [(r[0], r[1], now) for r in regs]
    )

    db.commit()


@app.cli.command('init-db')
def init_db_command():
    init_db()
    print('✅ Database initialised and seeded.')


# ═══════════════════════════════════════════════════════════════════════════
#  AUTH DECORATORS
# ═══════════════════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
#  CONTEXT PROCESSOR  — injects current_user into every template
# ═══════════════════════════════════════════════════════════════════════════

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if row:
            user = dict(row)
    return dict(current_user=user)


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_event_status(event_date_str, end_date_str, current_status):
    """Auto-derive event status from dates."""
    try:
        today = date.today()
        start = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        end = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else start
        if today < start:
            return 'upcoming'
        elif start <= today <= end:
            return 'ongoing'
        else:
            return 'completed'
    except Exception:
        return current_status


# ═══════════════════════════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def home():
    db = get_db()
    upcoming = db.execute(
        """SELECT e.*, c.name AS club_name, c.category,
           (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id) AS reg_count
           FROM events e JOIN clubs c ON e.club_id = c.id
           WHERE e.status = 'upcoming' AND c.status = 'approved'
           ORDER BY e.event_date ASC LIMIT 6"""
    ).fetchall()
    featured_clubs = db.execute(
        """SELECT c.*,
           (SELECT COUNT(*) FROM club_members cm WHERE cm.club_id = c.id) AS member_count
           FROM clubs c WHERE c.status = 'approved'
           ORDER BY member_count DESC LIMIT 4"""
    ).fetchall()
    stats = {
        'clubs':  db.execute("SELECT COUNT(*) FROM clubs WHERE status='approved'").fetchone()[0],
        'events': db.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        'students': db.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0],
        'registrations': db.execute("SELECT COUNT(*) FROM registrations").fetchone()[0],
    }
    return render_template('home.html', upcoming=upcoming, featured_clubs=featured_clubs, stats=stats)


# ── Auth ───────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['role']    = user['role']
            session['name']    = user['name']
            flash(f'Welcome back, {user["name"].split()[0]}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth.html', mode='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role     = request.form.get('role', 'student')

        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth.html', mode='register')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth.html', mode='register')
        if role not in ('student', 'club_admin'):
            role = 'student'

        db = get_db()
        if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            flash('Email already registered.', 'danger')
            return render_template('auth.html', mode='register')

        db.execute(
            "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?,?,?,?,?)",
            (name, email, generate_password_hash(password), role, datetime.now())
        )
        db.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('auth.html', mode='register')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ── Clubs ─────────────────────────────────────────────────────────────────

@app.route('/clubs')
def clubs():
    db = get_db()
    cat    = request.args.get('cat', '')
    search = request.args.get('q', '')
    query  = """SELECT c.*,
                (SELECT COUNT(*) FROM club_members cm WHERE cm.club_id = c.id) AS member_count,
                (SELECT COUNT(*) FROM events e WHERE e.club_id = c.id) AS event_count
                FROM clubs c WHERE c.status = 'approved'"""
    params = []
    if cat:
        query += " AND c.category = ?"; params.append(cat)
    if search:
        query += " AND (c.name LIKE ? OR c.description LIKE ?)"; params += [f'%{search}%', f'%{search}%']
    query += " ORDER BY member_count DESC"
    club_list = db.execute(query, params).fetchall()
    categories = db.execute("SELECT DISTINCT category FROM clubs WHERE status='approved'").fetchall()
    return render_template('clubs.html', clubs=club_list, categories=categories, selected_cat=cat, search=search)


@app.route('/clubs/<int:club_id>')
def club_detail(club_id):
    db = get_db()
    club = db.execute(
        """SELECT c.*,
           (SELECT COUNT(*) FROM club_members cm WHERE cm.club_id = c.id) AS member_count,
           u.name AS admin_name
           FROM clubs c LEFT JOIN users u ON c.admin_id = u.id
           WHERE c.id = ? AND c.status = 'approved'""",
        (club_id,)
    ).fetchone()
    if not club:
        flash('Club not found.', 'danger'); return redirect(url_for('clubs'))

    events = db.execute(
        """SELECT e.*,
           (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id) AS reg_count
           FROM events e WHERE e.club_id = ? ORDER BY e.event_date ASC""",
        (club_id,)
    ).fetchall()

    members = db.execute(
        """SELECT u.id, u.name, u.email, cm.joined_at
           FROM users u JOIN club_members cm ON u.id = cm.user_id
           WHERE cm.club_id = ? ORDER BY cm.joined_at DESC LIMIT 12""",
        (club_id,)
    ).fetchall()

    is_member = False
    if 'user_id' in session:
        is_member = bool(db.execute(
            "SELECT 1 FROM club_members WHERE user_id=? AND club_id=?",
            (session['user_id'], club_id)
        ).fetchone())

    return render_template('club_detail.html', club=club, events=events,
                           members=members, is_member=is_member)


# ── Events ────────────────────────────────────────────────────────────────

@app.route('/events')
def events():
    db = get_db()
    status = request.args.get('status', '')
    search = request.args.get('q', '')
    query  = """SELECT e.*, c.name AS club_name, c.category,
                (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id) AS reg_count
                FROM events e JOIN clubs c ON e.club_id = c.id
                WHERE c.status = 'approved'"""
    params = []
    if status:
        query += " AND e.status = ?"; params.append(status)
    if search:
        query += " AND (e.title LIKE ? OR e.description LIKE ?)"; params += [f'%{search}%', f'%{search}%']
    query += " ORDER BY e.event_date ASC"
    event_list = db.execute(query, params).fetchall()
    return render_template('events.html', events=event_list, selected_status=status, search=search)


@app.route('/events/<int:event_id>')
def event_detail(event_id):
    db = get_db()
    event = db.execute(
        """SELECT e.*, c.name AS club_name, c.category, c.id AS cid,
           (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id) AS reg_count
           FROM events e JOIN clubs c ON e.club_id = c.id
           WHERE e.id = ?""",
        (event_id,)
    ).fetchone()
    if not event:
        flash('Event not found.', 'danger'); return redirect(url_for('events'))

    is_registered = False
    if 'user_id' in session:
        is_registered = bool(db.execute(
            "SELECT 1 FROM registrations WHERE user_id=? AND event_id=?",
            (session['user_id'], event_id)
        ).fetchone())

    participants = []
    can_see_participants = (
        session.get('role') == 'super_admin' or
        (session.get('role') == 'club_admin' and
         db.execute("SELECT 1 FROM clubs WHERE id=? AND admin_id=?",
                    (event['club_id'], session.get('user_id'))).fetchone())
    )
    if can_see_participants:
        participants = db.execute(
            """SELECT u.name, u.email, r.registered_at
               FROM users u JOIN registrations r ON u.id = r.user_id
               WHERE r.event_id = ? ORDER BY r.registered_at""",
            (event_id,)
        ).fetchall()

    return render_template('event_detail.html', event=event,
                           is_registered=is_registered,
                           participants=participants,
                           can_see_participants=can_see_participants)


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD ROUTES  (login required)
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/dashboard')
@login_required
def dashboard():
    db   = get_db()
    uid  = session['user_id']
    role = session['role']

    if role == 'super_admin':
        data = {
            'total_users':   db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            'total_clubs':   db.execute("SELECT COUNT(*) FROM clubs").fetchone()[0],
            'total_events':  db.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            'total_regs':    db.execute("SELECT COUNT(*) FROM registrations").fetchone()[0],
            'pending_clubs': db.execute("SELECT * FROM clubs WHERE status='pending'").fetchall(),
            'recent_users':  db.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 8").fetchall(),
            'all_clubs':     db.execute(
                """SELECT c.*, u.name AS admin_name,
                   (SELECT COUNT(*) FROM club_members cm WHERE cm.club_id=c.id) AS member_count
                   FROM clubs c LEFT JOIN users u ON c.admin_id=u.id ORDER BY c.created_at DESC"""
            ).fetchall(),
            'all_events': db.execute(
                """SELECT e.*, c.name AS club_name,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id=e.id) AS reg_count
                   FROM events e JOIN clubs c ON e.club_id=c.id ORDER BY e.event_date DESC"""
            ).fetchall(),
        }
        return render_template('dashboard_admin.html', **data)

    elif role == 'club_admin':
        club = db.execute(
            """SELECT c.*,
               (SELECT COUNT(*) FROM club_members cm WHERE cm.club_id=c.id) AS member_count
               FROM clubs c WHERE c.admin_id=?""",
            (uid,)
        ).fetchone()
        my_events, members = [], []
        if club:
            my_events = db.execute(
                """SELECT e.*,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id=e.id) AS reg_count
                   FROM events e WHERE e.club_id=? ORDER BY e.event_date DESC""",
                (club['id'],)
            ).fetchall()
            members = db.execute(
                """SELECT u.id, u.name, u.email, cm.joined_at
                   FROM users u JOIN club_members cm ON u.id=cm.user_id
                   WHERE cm.club_id=? ORDER BY cm.joined_at DESC""",
                (club['id'],)
            ).fetchall()
        return render_template('dashboard_club_admin.html', club=club,
                               my_events=my_events, members=members)

    else:  # student
        my_clubs = db.execute(
            """SELECT c.*, cm.joined_at,
               (SELECT COUNT(*) FROM club_members x WHERE x.club_id=c.id) AS member_count
               FROM clubs c JOIN club_members cm ON c.id=cm.club_id
               WHERE cm.user_id=?""",
            (uid,)
        ).fetchall()
        my_events = db.execute(
            """SELECT e.*, c.name AS club_name, r.registered_at,
               (SELECT COUNT(*) FROM registrations x WHERE x.event_id=e.id) AS reg_count
               FROM events e JOIN clubs c ON e.club_id=c.id
               JOIN registrations r ON e.id=r.event_id
               WHERE r.user_id=? ORDER BY e.event_date ASC""",
            (uid,)
        ).fetchall()
        return render_template('dashboard_student.html',
                               my_clubs=my_clubs, my_events=my_events)


# ═══════════════════════════════════════════════════════════════════════════
#  ACTION ROUTES  (POST endpoints)
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/clubs/join/<int:club_id>', methods=['POST'])
@login_required
def join_club(club_id):
    db  = get_db()
    uid = session['user_id']
    club = db.execute("SELECT * FROM clubs WHERE id=? AND status='approved'", (club_id,)).fetchone()
    if not club:
        flash('Club not found.', 'danger')
    elif db.execute("SELECT 1 FROM club_members WHERE user_id=? AND club_id=?", (uid, club_id)).fetchone():
        flash('Already a member.', 'info')
    else:
        db.execute("INSERT INTO club_members (user_id, club_id, joined_at) VALUES (?,?,?)",
                   (uid, club_id, datetime.now()))
        db.commit()
        flash(f'Joined {club["name"]}!', 'success')
    return redirect(request.referrer or url_for('clubs'))


@app.route('/clubs/leave/<int:club_id>', methods=['POST'])
@login_required
def leave_club(club_id):
    db = get_db()
    db.execute("DELETE FROM club_members WHERE user_id=? AND club_id=?",
               (session['user_id'], club_id))
    db.commit()
    flash('Left the club.', 'info')
    return redirect(request.referrer or url_for('clubs'))


@app.route('/events/register/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    db  = get_db()
    uid = session['user_id']
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        flash('Event not found.', 'danger')
    elif event['status'] == 'completed':
        flash('This event has already completed.', 'warning')
    elif db.execute("SELECT 1 FROM registrations WHERE user_id=? AND event_id=?", (uid, event_id)).fetchone():
        flash('Already registered.', 'info')
    else:
        reg_count = db.execute("SELECT COUNT(*) FROM registrations WHERE event_id=?", (event_id,)).fetchone()[0]
        if reg_count >= event['max_participants']:
            flash('Event is full.', 'warning')
        else:
            db.execute("INSERT INTO registrations (user_id, event_id, registered_at) VALUES (?,?,?)",
                       (uid, event_id, datetime.now()))
            db.commit()
            flash(f'Registered for "{event["title"]}"!', 'success')
    return redirect(request.referrer or url_for('events'))


@app.route('/events/unregister/<int:event_id>', methods=['POST'])
@login_required
def unregister_event(event_id):
    db = get_db()
    db.execute("DELETE FROM registrations WHERE user_id=? AND event_id=?",
               (session['user_id'], event_id))
    db.commit()
    flash('Unregistered from event.', 'info')
    return redirect(request.referrer or url_for('dashboard'))


# ── Club Admin: Event CRUD ────────────────────────────────────────────────

@app.route('/manage/events/create', methods=['GET', 'POST'])
@role_required('club_admin', 'super_admin')
def create_event():
    db   = get_db()
    uid  = session['user_id']
    role = session['role']

    if role == 'super_admin':
        clubs = db.execute("SELECT id, name FROM clubs WHERE status='approved'").fetchall()
    else:
        clubs = db.execute("SELECT id, name FROM clubs WHERE admin_id=? AND status='approved'", (uid,)).fetchall()

    if request.method == 'POST':
        club_id   = int(request.form.get('club_id'))
        title     = request.form.get('title', '').strip()
        desc      = request.form.get('description', '').strip()
        ev_date   = request.form.get('event_date', '')
        ev_time   = request.form.get('event_time', '')
        end_date  = request.form.get('end_date', '')
        venue     = request.form.get('venue', '').strip()
        max_p     = int(request.form.get('max_participants', 50))
        category  = request.form.get('category', '')

        if not all([title, desc, ev_date, ev_time, venue]):
            flash('All required fields must be filled.', 'danger')
            return render_template('event_form.html', clubs=clubs, mode='create')

        status = get_event_status(ev_date, end_date, 'upcoming')
        db.execute(
            """INSERT INTO events (club_id, title, description, event_date, event_time,
               end_date, venue, max_participants, status, category, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (club_id, title, desc, ev_date, ev_time, end_date or ev_date,
             venue, max_p, status, category, datetime.now())
        )
        db.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('event_form.html', clubs=clubs, mode='create')


@app.route('/manage/events/edit/<int:event_id>', methods=['GET', 'POST'])
@role_required('club_admin', 'super_admin')
def edit_event(event_id):
    db   = get_db()
    uid  = session['user_id']
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        flash('Event not found.', 'danger'); return redirect(url_for('dashboard'))

    # Only allow admin of that club (or super admin)
    if session['role'] != 'super_admin':
        club = db.execute("SELECT 1 FROM clubs WHERE id=? AND admin_id=?",
                          (event['club_id'], uid)).fetchone()
        if not club:
            flash('Access denied.', 'danger'); return redirect(url_for('dashboard'))

    clubs = db.execute("SELECT id, name FROM clubs WHERE status='approved'").fetchall()

    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        desc     = request.form.get('description', '').strip()
        ev_date  = request.form.get('event_date', '')
        ev_time  = request.form.get('event_time', '')
        end_date = request.form.get('end_date', '')
        venue    = request.form.get('venue', '').strip()
        max_p    = int(request.form.get('max_participants', 50))
        category = request.form.get('category', '')
        status   = get_event_status(ev_date, end_date, 'upcoming')

        db.execute(
            """UPDATE events SET title=?, description=?, event_date=?, event_time=?,
               end_date=?, venue=?, max_participants=?, status=?, category=?
               WHERE id=?""",
            (title, desc, ev_date, ev_time, end_date or ev_date,
             venue, max_p, status, category, event_id)
        )
        db.commit()
        flash('Event updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('event_form.html', clubs=clubs, mode='edit', event=event)


@app.route('/manage/events/delete/<int:event_id>', methods=['POST'])
@role_required('club_admin', 'super_admin')
def delete_event(event_id):
    db  = get_db()
    uid = session['user_id']
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        flash('Event not found.', 'danger'); return redirect(url_for('dashboard'))
    if session['role'] != 'super_admin':
        club = db.execute("SELECT 1 FROM clubs WHERE id=? AND admin_id=?",
                          (event['club_id'], uid)).fetchone()
        if not club:
            flash('Access denied.', 'danger'); return redirect(url_for('dashboard'))
    db.execute("DELETE FROM registrations WHERE event_id=?", (event_id,))
    db.execute("DELETE FROM events WHERE id=?", (event_id,))
    db.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('dashboard'))


# ── Club Admin: Club Profile ───────────────────────────────────────────────

@app.route('/manage/club/edit', methods=['GET', 'POST'])
@role_required('club_admin')
def edit_club():
    db   = get_db()
    uid  = session['user_id']
    club = db.execute("SELECT * FROM clubs WHERE admin_id=?", (uid,)).fetchone()
    if not club:
        flash('No club found. Create one first.', 'warning')
        return redirect(url_for('create_club'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        desc     = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        db.execute("UPDATE clubs SET name=?, description=?, category=? WHERE id=?",
                   (name, desc, category, club['id']))
        db.commit()
        flash('Club profile updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('club_form.html', club=club, mode='edit')


@app.route('/manage/club/create', methods=['GET', 'POST'])
@role_required('club_admin')
def create_club():
    db  = get_db()
    uid = session['user_id']
    if db.execute("SELECT 1 FROM clubs WHERE admin_id=?", (uid,)).fetchone():
        flash('You already manage a club.', 'warning')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        desc     = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        if not name or not desc:
            flash('Name and description required.', 'danger')
            return render_template('club_form.html', club=None, mode='create')
        db.execute(
            "INSERT INTO clubs (name, category, description, admin_id, status, created_at) VALUES (?,?,?,?,?,?)",
            (name, category, desc, uid, 'pending', datetime.now())
        )
        db.commit()
        flash('Club submitted for approval!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('club_form.html', club=None, mode='create')


# ── Super Admin Actions ────────────────────────────────────────────────────

@app.route('/admin/clubs/<action>/<int:club_id>', methods=['POST'])
@role_required('super_admin')
def admin_club_action(action, club_id):
    db = get_db()
    if action == 'approve':
        db.execute("UPDATE clubs SET status='approved' WHERE id=?", (club_id,))
        flash('Club approved.', 'success')
    elif action == 'reject':
        db.execute("UPDATE clubs SET status='rejected' WHERE id=?", (club_id,))
        flash('Club rejected.', 'info')
    elif action == 'delete':
        db.execute("DELETE FROM club_members WHERE club_id=?", (club_id,))
        db.execute("DELETE FROM registrations WHERE event_id IN (SELECT id FROM events WHERE club_id=?)", (club_id,))
        db.execute("DELETE FROM events WHERE club_id=?", (club_id,))
        db.execute("DELETE FROM clubs WHERE id=?", (club_id,))
        flash('Club deleted.', 'info')
    db.commit()
    return redirect(url_for('dashboard'))


@app.route('/admin/users/deactivate/<int:user_id>', methods=['POST'])
@role_required('super_admin')
def deactivate_user(user_id):
    db = get_db()
    db.execute("UPDATE users SET is_active=0 WHERE id=?", (user_id,))
    db.commit()
    flash('User deactivated.', 'info')
    return redirect(url_for('dashboard'))


# ── Remove club member (club admin) ───────────────────────────────────────

@app.route('/manage/members/remove/<int:user_id>', methods=['POST'])
@role_required('club_admin', 'super_admin')
def remove_member(user_id):
    db  = get_db()
    uid = session['user_id']
    club = db.execute("SELECT * FROM clubs WHERE admin_id=?", (uid,)).fetchone()
    if not club and session['role'] != 'super_admin':
        flash('Access denied.', 'danger'); return redirect(url_for('dashboard'))
    club_id = request.form.get('club_id')
    db.execute("DELETE FROM club_members WHERE user_id=? AND club_id=?", (user_id, club_id))
    db.commit()
    flash('Member removed.', 'info')
    return redirect(url_for('dashboard'))


# ─── Error Handlers ───────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Server error.'), 500


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['DATABASE']):
            init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)