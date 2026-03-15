# -*- coding: utf-8 -*-
"""
Flask应用入口
"""
import os
import sys
import webbrowser
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, CORS_ORIGINS
from models import db
from api import api_bp


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发和打包环境"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def create_app():
    """创建Flask应用实例"""
    static_folder = get_resource_path('static')
    template_folder = get_resource_path('static')
    
    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
    
    # 配置
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['JSON_AS_ASCII'] = False
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, origins=CORS_ORIGINS)
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'code': 404, 'message': '资源不存在'}), 404
        else:
            return send_from_directory(static_folder, 'index.html')
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500
    
    # 健康检查
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok', 'message': '服务正常运行'})
    
    # 根路由和前端路由
    @app.route('/')
    def index():
        return send_from_directory(static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if path.startswith('api/'):
            return jsonify({'code': 404, 'message': '资源不存在'}), 404
        if os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            return send_from_directory(static_folder, 'index.html')
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    import threading
    import time
    
    with app.app_context():
        db.create_all()
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:5001')
    
    if not os.environ.get('DISABLE_AUTO_OPEN'):
        threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=False, host='127.0.0.1', port=5001)
