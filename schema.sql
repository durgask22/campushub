-- ═══════════════════════════════════════════════════════════════════════════
--  CampusHub — Database Schema
--  SQLite (compatible with MySQL with minor syntax adjustments)
-- ═══════════════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = ON;

-- ─── Users ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'student'
                            CHECK(role IN ('student','club_admin','super_admin')),
    is_active     INTEGER NOT NULL DEFAULT 1,
    bio           TEXT,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users(role);

-- ─── Clubs ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clubs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    category    TEXT    NOT NULL,
    description TEXT    NOT NULL,
    admin_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status      TEXT    NOT NULL DEFAULT 'pending'
                          CHECK(status IN ('pending','approved','rejected')),
    logo_url    TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clubs_status   ON clubs(status);
CREATE INDEX IF NOT EXISTS idx_clubs_category ON clubs(category);

-- ─── Events ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id          INTEGER NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    title            TEXT    NOT NULL,
    description      TEXT    NOT NULL,
    event_date       TEXT    NOT NULL,   -- ISO date: YYYY-MM-DD
    event_time       TEXT    NOT NULL,   -- HH:MM
    end_date         TEXT,               -- ISO date
    venue            TEXT    NOT NULL,
    max_participants INTEGER NOT NULL DEFAULT 50,
    status           TEXT    NOT NULL DEFAULT 'upcoming'
                               CHECK(status IN ('upcoming','ongoing','completed')),
    category         TEXT,
    image_url        TEXT,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_club_id ON events(club_id);
CREATE INDEX IF NOT EXISTS idx_events_status  ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_date    ON events(event_date);

-- ─── Registrations ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS registrations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    event_id      INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_reg_user_id  ON registrations(user_id);
CREATE INDEX IF NOT EXISTS idx_reg_event_id ON registrations(event_id);

-- ─── Club Members ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS club_members (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    club_id   INTEGER NOT NULL REFERENCES clubs(id)  ON DELETE CASCADE,
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, club_id)
);

CREATE INDEX IF NOT EXISTS idx_cm_user_id ON club_members(user_id);
CREATE INDEX IF NOT EXISTS idx_cm_club_id ON club_members(club_id);