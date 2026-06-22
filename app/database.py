import os
import importlib
import random

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": os.getenv("MYSQL_DATABASE", "language_learner"),
}

SEED_DICTIONARY_ENTRIES = [
    ("Haus", "house"),
    ("Wasser", "water"),
    ("Buch", "book"),
    ("Katze", "cat"),
    ("Brot", "bread"),
    ("Danke", "thank you"),
    ("Bitte", "please"),
    ("Freund", "friend"),
    ("Straße", "street"),
    ("Schule", "school"),
    ("Sonne", "sun"),
    ("Apfel", "apple"),
    ("Liebe", "love"),
    ("Zeit", "time"),
    ("Morgen", "morning"),
]

class DatabaseUnavailableError(RuntimeError):
    pass


def get_database_connection():
    mysql_connector = importlib.import_module("mysql.connector")
    return mysql_connector.connect(**DB_CONFIG)


def ensure_dictionary_database_exists():
    mysql_connector = importlib.import_module("mysql.connector")
    try:
        connection = mysql_connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
    except Exception as exc:
        raise DatabaseUnavailableError(
            f"MySQL is unavailable at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
            "Check the database container, host, and port settings."
        ) from exc
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def initialize_dictionary_database():
    ensure_dictionary_database_exists()
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dictionary_entries (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        german_word VARCHAR(255) NOT NULL,
                        english_translation VARCHAR(255) NOT NULL
                    )
                    """
                )
                cursor.execute("SELECT COUNT(*) FROM dictionary_entries")
                existing_count = cursor.fetchone()[0]
                if existing_count == 0:
                    seed_entries = random.sample(SEED_DICTIONARY_ENTRIES, 10)
                    cursor.executemany(
                        "INSERT INTO dictionary_entries (german_word, english_translation) VALUES (%s, %s)",
                        seed_entries,
                    )
            connection.commit()
    except DatabaseUnavailableError:
        raise
    except Exception as exc:
        raise DatabaseUnavailableError(
            f"MySQL is unavailable at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
            "Check the database container, host, and port settings."
        ) from exc