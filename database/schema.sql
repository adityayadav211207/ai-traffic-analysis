-- ==========================================
-- USERS TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    role TEXT NOT NULL

);

-- ==========================================
-- DATASETS TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS datasets (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    filename TEXT NOT NULL,

    raw_path TEXT NOT NULL,

    clean_path TEXT NOT NULL,

    uploaded_by TEXT NOT NULL,

    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    is_active INTEGER DEFAULT 0

);

CREATE UNIQUE INDEX IF NOT EXISTS one_admin_account
ON users (role)
WHERE role = 'admin';