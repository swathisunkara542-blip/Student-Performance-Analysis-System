"""Configuration is kept separate from application code and read from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "student_performance")
    LOW_PERFORMER_THRESHOLD = float(os.getenv("LOW_PERFORMER_THRESHOLD", "40"))
    CHART_DIR = os.getenv("CHART_DIR", "charts")
