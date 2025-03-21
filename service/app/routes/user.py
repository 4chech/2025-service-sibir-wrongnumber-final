from flask import Blueprint, render_template, redirect, flash, url_for, request, session, jsonify, current_app
from flask_login import login_user, logout_user
import hashlib
import itsdangerous
import time

from ..functions import save_picture, generate_random_phone_number
from ..forms import RegistrationForm, LoginForm
from ..extensions import db, bcrypt
from ..models.user import User
from ..models.number import Number

user = Blueprint('user', __name__) 


def set_number(user_id, flag, login):
    phone_number = generate_random_phone_number()
    new_number = Number(owner_id=user_id, secret=flag, phone_number=phone_number, owner_login=login)
    db.session.add(new_number)
    db.session.commit()
    return new_number


def generate_user_secret(user_data):
    user_string = f"{user_data.login}{user_data.id}"
    return hashlib.md5(user_string.encode()).hexdigest()[:8]


@user.route('/user/register', methods=['GET', 'POST'])
def register():
    if request.is_json:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty request body"}), 400
            
        form_data = {
            'login': data.get('login'),
            'password': data.get('password'),
            'flag': data.get('flag'),
            'avatar': data.get('avatar', 'default.jpg')
        }
        
        for key, value in data.items():
            if key not in form_data:
                form_data[key] = value
    else:
        form = RegistrationForm()
        if form.validate_on_submit():
            form_data = {
                'login': form.login.data,
                'password': form.password.data,
                'flag': form.flag.data,
                'avatar': save_picture(form.avatar.data),
                'status': 'user'
            }
        else:
            return render_template('user/register.html', form=form)

    try:
        hashed_password = bcrypt.generate_password_hash(form_data['password']).decode('utf-8')
        form_data['password'] = hashed_password
        
        user = User(**form_data)
        db.session.add(user)
        db.session.commit()
        
        set_number(user.id, form_data['flag'], form_data['login'])
        
        if request.is_json:
            return jsonify({
                "message": "User registered successfully",
                "user_id": user.id,
                "login": user.login,
                "status": user.status
            }), 201
        else:
            flash(f"Поздравляем, {form_data['login']}! Вы успешно зарегистрированы", "success")
            return redirect(url_for('user.login'))
            
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({"error": str(e)}), 400
        else:
            flash(f"При регистрации произошла ошибка", "danger")
            return render_template('user/register.html', form=form)


@user.route('/user/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session.clear()
            login_user(user, remember=form.remember.data)
            session['user_id'] = user.id
            session['user_status'] = user.status
            session['_fresh'] = True  # Добавляем стандартные поля Flask-Login
            session['_id'] = '10151015'  # Добавляем фиксированный идентификатор
            next_page = request.args.get('next')
            flash(f"Поздравляем, {form.login.data}! Вы успешно авторизованы", "success")
            return redirect(next_page) if next_page else redirect(url_for('post.all'))
        else:
            flash(f"Ошибка входа. Пожалуйста проверьте логин и пароль!", category='danger')
    return render_template('user/login.html', form=form)


@user.route('/user/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('post.all'))


@user.route('/create_admin', methods=['GET'])
def create_admin():
    try:
        # Проверяем, существует ли уже администратор
        admin = User.query.filter_by(login='admin').first()
        if admin:
            return "admin already exists"
        
        # Создаем нового администратора
        hashed_password = bcrypt.generate_password_hash('SuperAdminPassword!@123').decode('utf-8')
        admin = User(
            login='admin',
            password=hashed_password,
            status='admin',
            flag='SIBIRCTF{admin_is_here}',
            avatar='default.jpg'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        # Создаем номер для администратора
        set_number(admin.id, admin.flag, admin.login)
        
    except Exception as e:
        db.session.rollback()
        print(f'Ошибка при создании администратора: {str(e)}')


@user.route('/api/v1/session/<user_id>', methods=['GET'])
def get_session(user_id):
    """API endpoint для получения сессии пользователя"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    session_data = {
        'user_id': user.id,
        'user_status': user.status,
        '_fresh': True,
        '_id': '10151015'
    }
    session_token = itsdangerous.URLSafeTimedSerializer(current_app.config['SECRET_KEY']).dumps(session_data)
    
    return jsonify({
        "session": session_token,
        "user_id": user.id,
        "status": user.status
    })

@user.route('/api/v1/verify_session', methods=['POST'])
def verify_session_endpoint():
    """API endpoint для проверки сессии"""
    data = request.get_json()
    if not data or 'session' not in data:
        return jsonify({"error": "No session data provided"}), 400
    
    try:
        session_data = itsdangerous.URLSafeTimedSerializer(current_app.config['SECRET_KEY']).loads(data['session'])
        return jsonify({
            "valid": True,
            "user_id": session_data['user_id'],
            "status": session_data['user_status']
        })
    except:
        return jsonify({"error": "Invalid session"}), 400



