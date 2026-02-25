#!/bin/sh
echo "=== 运行数据库自动迁移 ==="
python backend/auto_migrate.py

echo "=== 启动应用 ==="
exec gunicorn -w 2 --threads 4 -b 0.0.0.0:8080 --timeout 300 --preload app:app --chdir backend
