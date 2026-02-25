#!/bin/sh
echo "=== 清理旧数据库 ==="
rm -f backend/shu_prophet.db

echo "=== 启动应用 ==="
exec gunicorn -w 2 --threads 4 -b 0.0.0.0:8080 --timeout 300 --preload app:app --chdir backend
