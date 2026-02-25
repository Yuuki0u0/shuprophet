#!/bin/sh
echo "=== 运行数据库自动迁移 ==="
python backend/auto_migrate.py

echo "=== 启动应用 ==="
exec gunicorn -w 2 -b 0.0.0.0:8080 app:app --chdir backend
