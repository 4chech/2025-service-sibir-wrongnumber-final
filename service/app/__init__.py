from flask import Flask, Config, session
from flask_login import LoginManager

from .forms import LoginForm
from .extensions import db, migrate, login_manager
from .config import Config

from .routes.user import user, create_admin
from .routes.post import post
from .routes.review import review
from .routes.numbers import numbers


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(review)
    app.register_blueprint(numbers)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # LOGIN MANAGER
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Вы не можете получить доступ к данной странице. Нужно сначала войти.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        db.create_all()
        create_admin()

    return app