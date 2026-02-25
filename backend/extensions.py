import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'shu-prophet-secret-key-2024')

# 管理员密码：通过环境变量设置，源码里不存明文
# 部署时设置: export ADMIN_PASSWORD=你的密码
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', None)
