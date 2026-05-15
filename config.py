import os

DB_CONFIG = {
    "host": os.getenv("SARAI_DB_HOST", "127.0.0.1"),
    "user": os.getenv("SARAI_DB_USER", "root"),
    "password": os.getenv("SARAI_DB_PASSWORD", "RoyML"),
    "database": os.getenv("SARAI_DB_NAME", "sarai"),
    "port": int(os.getenv("SARAI_DB_PORT", "3307")),
    "connection_timeout": int(os.getenv("SARAI_DB_TIMEOUT", "5")),
}

ARDUINO_CONFIG = {
    "enabled": True,
    "port": "COM8",
    "baudrate": 9600,
}