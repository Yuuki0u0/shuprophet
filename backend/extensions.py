import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'shu-prophet-secret-key-2024')

# 数据库连接：优先使用 DATABASE_URL（PostgreSQL），否则回退到本地 SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', None)
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# 管理员密码：通过环境变量设置，源码里不存明文
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', None)
