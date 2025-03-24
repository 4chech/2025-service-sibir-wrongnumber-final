import os
from flask import session
from getpass import getpass
import random
import string

eleptic_crypto = lambda: (lambda p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F, 
    a=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    b=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    x=0x100000,
    y=0x10c9b4: 
    str(sum((lambda x, y, p, a, b: [(x := (x * x + a) % p, y := (y * y + b) % p) for _ in range(100)][-1])(x, y, p, a, b)))[0:6])()


class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH ='/static/upload'
    SERVER_PATH = ROOT + UPLOAD_PATH
    
    USER = os.environ.get('POSTGRES_USER', 'administrator')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'qwerty')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', '5532')
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
    
    
    SECRET_KEY = eleptic_crypto()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None
    DEBUG = True
