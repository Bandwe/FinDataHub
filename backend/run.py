# -*- coding: utf-8 -*-
"""
应用启动脚本
"""
from app import app, create_app
from models import db

if __name__ == '__main__':
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")
    
    print("启动服务器: http://127.0.0.1:5002")
    app.run(debug=True, host='0.0.0.0', port=5002)
