import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
local_env_path = os.path.join(basedir, "instance", ".env")


def load_local_env(path):
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


def get_float_env(name, default):
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return float(default)


load_local_env(local_env_path)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-prod")
    PARKING_MAP_CENTER_LAT = get_float_env("PARKING_MAP_CENTER_LAT", "-1.286389")
    PARKING_MAP_CENTER_LNG = get_float_env("PARKING_MAP_CENTER_LNG", "36.817223")
    
    # SQLite: Use absolute path to avoid "unable to open file" errors
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(basedir, 'instance', 'parking.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pooling (used when migrating to PostgreSQL)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    }
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
