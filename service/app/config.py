import os
from flask import session
from getpass import getpass
import random
import string

def generate_weak_secret():
    # Генерируем слабый секретный ключ из 8 символов
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH ='/static/upload'
    SERVER_PATH = ROOT + UPLOAD_PATH
    
    USER = os.environ.get('POSTGRES_USER', 'administrator')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'qwerty')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', '5432')
    DB = os.environ.get('POSTGRES_DB', 'wrongnumber')

    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'client_encoding': 'utf8',
            'options': '-c client_encoding=utf8 -c timezone=UTC',
            'application_name': 'sibir_service',
            'connect_timeout': 10
        }
    }
    
    # Слабый секретный ключ для CTF
    SECRET_KEY = '10151015'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Настройки сессии для CTF
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None
    
    DEBUG = True
