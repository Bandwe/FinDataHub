import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 数据库配置
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DATA_DIR, "findata.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# CORS配置
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5001"]

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
