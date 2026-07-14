# -*- coding: utf-8 -*-
"""
应用启动脚本
"""
import os

from app import app
from migrations import run_sqlite_migrations
from models import db

if __name__ == '__main__':
    with app.app_context():
        # 创建所有表
        db.create_all()
        run_sqlite_migrations(app.config['SQLALCHEMY_DATABASE_URI'])
        print("数据库表创建完成")

    host = os.environ.get('FINDATA_HOST', '127.0.0.1')
    port = int(os.environ.get('FINDATA_PORT', '5002'))
    debug = os.environ.get('FINDATA_DEBUG', '').lower() in {'1', 'true', 'yes'}

    print(f"启动服务器: http://{host}:{port}")
    app.run(debug=debug, host=host, port=port, use_reloader=debug)
