from flask import Blueprint, render_template, redirect, flash, url_for, request, session, jsonify, current_app
from flask_login import login_user, logout_user
import hashlib
import itsdangerous
import time
import os
from werkzeug.utils import secure_filename

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


@user.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            login = data.get('login')
            password = data.get('password')
            flag = data.get('flag')
            status = data.get('status', 'user')
            
            if User.query.filter_by(login=login).first():
                return jsonify({"error": "Login already exists"}), 400
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            user = User(
                login=login,
                password=hashed_password,
                flag=flag,
                name=login,
                status=status,
                avatar='default.jpg'
            )
            
            try:
                db.session.add(user)
                db.session.commit()
                
                fake_number = generate_random_phone_number()
                number = Number(
                    owner_id=user.id,
                    phone_number=fake_number,
                    secret=flag,
                    owner_login=login
                )
                
                db.session.add(number)
                db.session.commit()
                
                return jsonify({
                    "message": "Registration successful",
                    "user_id": user.id,
                    "login": user.login,
                    "status": user.status
                }), 200
                
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500
        
        
        login = request.form.get('login')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        flag = request.form.get('flag')
        avatar = request.files.get('avatar')
        
        if User.query.filter_by(login=login).first():
            flash('Этот логин уже занят')
            return redirect(url_for('user.register'))
            
        if password != confirm_password:
            flash('Пароли не совпадают')
            return redirect(url_for('user.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        
        avatar_filename = None
        if avatar:
            avatar_filename = save_picture(avatar)
            if avatar_filename:
                avatar_filename = f'upload/{avatar_filename}'
        
        user = User(
            login=login,
            password=hashed_password,
            flag=flag,
            name=login,
            status='user',  
            avatar=avatar_filename or 'default.jpg'
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
           
            fake_number = generate_random_phone_number()
            number = Number(
                owner_id=user.id,
                phone_number=fake_number,
                secret=flag,
                owner_login=login
            )
            
            db.session.add(number)
            db.session.commit()
            
            flash('Регистрация успешна!')
            return redirect(url_for('user.login'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при регистрации')
            print(str(e))
            return redirect(url_for('user.register'))
        
    return render_template('user/register.html')


@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(login=login).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_status'] = user.status
            session['login'] = user.login
            return redirect(url_for('post.all'))
        flash('Неверный логин или пароль')
    return render_template('user/login.html')


@user.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))


@user.route('/create_admin', methods=['GET'])
def create_admin():
    try:
        
        admin = User.query.filter_by(login='admin').first()
        if admin:
            return "admin already exists"
        
        
        hashed_password = bcrypt.generate_password_hash('SuperAdminSecretPassword').decode('utf-8')
        admin = User(
            login='admin',
            password=hashed_password,
            status='admin',
            flag='sibirctf2025{admin_flag}',
            name='Admin'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        
        set_number(admin.id, admin.flag, admin.login)
        
    except Exception as e:
        db.session.rollback()
        print(f'Ошибка при создании администратора: {str(e)}')


@user.route('/api/v1/session/<int:user_id>')
def get_session(user_id):
    user = User.query.get_or_404(user_id)
    
    
    session_data = {
        'user_id': user.id,
        'user_status': user.status,
        'login': user.login
    }
    
    
    serializer = current_app.session_interface.get_signing_serializer(current_app)
    session_cookie = serializer.dumps(dict(session_data))
    
    return jsonify({
        'session_cookie': session_cookie,
        'user_id': user.id,
        'user_status': user.status,
        'login': user.login
    })


@user.route('/api/v1/session/verify', methods=['POST'])
def verify_session_endpoint():
    data = request.get_json()
    if not data or 'user_id' not in data or 'user_status' not in data:
        return jsonify({'error': 'Invalid session data'}), 400
    
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    session['user_id'] = data['user_id']
    session['user_status'] = data['user_status']
    session['login'] = user.login
    return jsonify({'message': 'Session verified'})



