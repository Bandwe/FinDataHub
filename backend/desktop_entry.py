# -*- coding: utf-8 -*-
"""
Desktop package entry point.

The source server uses backend/run.py. This entry keeps packaged builds stable:
no reloader, local-only binding, database migration at startup, and optional
browser auto-open.
"""
import os
import threading
import time
import webbrowser

from app import app
from migrations import run_sqlite_migrations
from models import db


def init_database():
    with app.app_context():
        db.create_all()
        run_sqlite_migrations(app.config['SQLALCHEMY_DATABASE_URI'])


def open_browser_later(host, port):
    time.sleep(1.5)
    webbrowser.open(f'http://{host}:{port}')


if __name__ == '__main__':
    init_database()

    host = os.environ.get('FINDATA_HOST', '127.0.0.1')
    port = int(os.environ.get('FINDATA_PORT', '5001'))

    if not os.environ.get('DISABLE_AUTO_OPEN'):
        threading.Thread(target=open_browser_later, args=(host, port), daemon=True).start()

    print(f'FinDataHub is running at http://{host}:{port}')
    app.run(debug=False, host=host, port=port, use_reloader=False)
