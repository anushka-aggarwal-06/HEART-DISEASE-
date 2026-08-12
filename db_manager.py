"""
db_manager.py
-------------
Handles all persistence for the Authentication module using SQLite.
Passwords are hashed with bcrypt before ever touching the database.
"""

import sqlite3
import os
import bcrypt
from datetime import datetime


class DatabaseManager:
    """Encapsulates every database operation needed by the auth module."""

    def __init__(self, db_name: str = "heartcare.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self._create_tables()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Create the users table automatically if it does not exist,
        and migrate older databases that pre-date the last_login column."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name     TEXT NOT NULL,
                    email         TEXT NOT NULL UNIQUE,
                    phone         TEXT NOT NULL,
                    age           INTEGER NOT NULL,
                    gender        TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at    TEXT NOT NULL,
                    last_login    TEXT
                )
                """
            )
            existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
            if "last_login" not in existing_cols:
                conn.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
            conn.commit()

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------
    @staticmethod
    def hash_password(plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except (ValueError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def email_exists(self, email: str) -> bool:
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "SELECT 1 FROM users WHERE email = ? LIMIT 1", (email.strip().lower(),)
                )
                return cur.fetchone() is not None
        except sqlite3.Error:
            # If we can't reach the database, fail safe: let the INSERT's
            # UNIQUE constraint be the final word rather than blocking here.
            return False

    def create_user(self, full_name, email, phone, age, gender, password) -> tuple:
        """
        Insert a new user with a securely hashed password.
        Returns (success: bool, message: str).
        """
        email = email.strip().lower()

        if self.email_exists(email):
            return False, "An account with this email already exists."

        password_hash = self.hash_password(password)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO users
                        (full_name, email, phone, age, gender, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (full_name.strip(), email, phone.strip(), int(age), gender, password_hash, created_at),
                )
                conn.commit()
            return True, "Account created successfully."
        except sqlite3.IntegrityError:
            return False, "An account with this email already exists."
        except sqlite3.Error as exc:
            return False, f"Database error: {exc}"

    def get_user_by_email(self, email: str):
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM users WHERE email = ? LIMIT 1", (email.strip().lower(),)
            )
            return cur.fetchone()

    def authenticate(self, email: str, password: str) -> tuple:
        """
        Verify credentials.
        Returns (success: bool, message: str, user_row: sqlite3.Row | None).

        Intentionally returns the SAME generic message whether the email
        doesn't exist or the password is wrong, so the app never reveals
        whether a given email is registered.
        """
        generic_failure = "Invalid email or password.", None
        try:
            user = self.get_user_by_email(email)
        except sqlite3.Error:
            return (False, "We couldn't reach the database. Please try again.", None)

        if user is None or not self.verify_password(password, user["password_hash"]):
            return (False,) + generic_failure

        self._update_last_login(user["id"])
        # Re-fetch so the returned row reflects the new last_login value.
        user = self.get_user_by_email(email)
        return True, "Login successful.", user

    def _update_last_login(self, user_id: int):
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
                )
                conn.commit()
        except sqlite3.Error:
            pass  # Last-login tracking is best-effort; never block login on it.
