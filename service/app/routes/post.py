import random
from flask import Blueprint, render_template, request, redirect, abort, flash, current_app, send_file, session, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from functools import wraps

from ..functions import save_picture
from ..forms import CarCreateForm
from ..models.user import User
from ..models.number import Number
from ..extensions import db
from ..models.post import Post
from ..models.review import Review


post = Blueprint('post', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function


@post.route('/', methods=['POST', 'GET'])
def all():
    posts = Post.query.order_by(Post.date.desc()).limit(30).all()
    for post in posts:
        if post.valuer:
            valuer_user = User.query.get(post.valuer)
            if valuer_user:
                
                post.valuer_login = valuer_user.login
                post.valuer_user = valuer_user
            else:
                post.valuer_login = "Неизвестный оценщик"
                post.valuer_user = None
        else:
            post.valuer_login = "Нет оценщика"
            post.valuer_user = None
    return render_template('post/all.html', posts=posts)


@post.route('/post/create', methods=['POST', 'GET'])
@login_required
def create():
    form = CarCreateForm()
    if request.method == 'POST':
        car_mark = request.form.get('car_mark')
        description = request.form.get('description')
        speed = request.form.get('speed')
        price_sum = random.randint(10000, 1000000)
        price_string = "Euro Dollars"
        price = f"{price_sum} {price_string}"
        handling = request.form.get('handling')
        durability = request.form.get('durability')
        fuel_consumption = request.form.get('fuel_consumption')
        seating_capacity = request.form.get('seating_capacity')
        customizations = request.form.get('customizations')
        
        
        try:
            speed = int(speed)
            handling = int(handling)
            durability = int(durability)
            fuel_consumption = float(fuel_consumption)
            seating_capacity = int(seating_capacity)
            
            if not (1 <= speed <= 500):
                flash('Скорость должна быть от 1 до 500 км/ч', 'danger')
                return redirect(url_for('post.create'))
                
            if not (1 <= handling <= 10):
                flash('Управляемость должна быть от 1 до 10', 'danger')
                return redirect(url_for('post.create'))
                
            if not (1 <= durability <= 10):
                flash('Прочность должна быть от 1 до 10', 'danger')
                return redirect(url_for('post.create'))
                
            if not (1 <= fuel_consumption <= 10):
                flash('Расход топлива должен быть от 1 до 10 л/100км', 'danger')
                return redirect(url_for('post.create'))
                
            if not (1 <= seating_capacity <= 8):
                flash('Количество мест должно быть от 1 до 8', 'danger')
                return redirect(url_for('post.create'))
                
        except (ValueError, TypeError):
            flash('Пожалуйста, введите корректные числовые значения', 'danger')
            return redirect(url_for('post.create'))
            
        
        picture = request.files.get('picture')
        if not picture:
            flash("Пожалуйста, загрузите изображение", "danger")
            return redirect(url_for('post.create'))
            
        picture_filename = save_picture(picture)
        if not picture_filename:
            flash("Пожалуйста, загрузите изображение в формате JPG, JPEG или PNG", "danger")
            return redirect(url_for('post.create'))
            
        user_number = Number.query.filter_by(owner_id=session['user_id']).first()
        
        
        valuers = User.query.filter(
            User.id != session['user_id'],
            User.status != 'admin'
        ).all()

        if not valuers:
            flash("Нет доступных оценщиков для назначения", "danger")
            return redirect(url_for('post.all'))

        
        valuer = random.choice(valuers)
        
        post = Post(
            owner=session['user_id'],
            car_mark=car_mark,
            description=description,
            speed=speed,
            price=price,
            handling=handling,
            durability=durability,
            fuel_consumption=fuel_consumption,
            seating_capacity=seating_capacity,
            customizations=customizations,
            valuer=valuer.id,
            picture=f'upload/{picture_filename}',
            number=user_number
        )
        
        try:
            db.session.add(post)
            db.session.commit()
            flash('Публикация успешно создана', 'success')
            return redirect(url_for('post.all'))
        except Exception as E:
            db.session.rollback()
            print(str(E))
            flash("Произошла ошибка при создании публикации", "danger")
            return redirect(url_for('post.create'))

    return render_template('post/create.html', form=form)



@post.route('/post/<int:id>/update', methods=['POST', 'GET'])
@login_required
def update(id):
    post = Post.query.get(id)
    if post.seller.id == session['user_id']:
        form = CarCreateForm()
        if request.method == 'POST':
            car_mark = request.form.get('car_mark')
            description = request.form.get('description')
            speed = request.form.get('speed')
            handling = request.form.get('handling')
            durability = request.form.get('durability')
            fuel_consumption = request.form.get('fuel_consumption')
            seating_capacity = request.form.get('seating_capacity')
            customizations = request.form.get('customizations')

            
            try:
                speed = int(speed)
                handling = int(handling)
                durability = int(durability)
                fuel_consumption = float(fuel_consumption)
                seating_capacity = int(seating_capacity)
                
                if not (1 <= speed <= 500):
                    flash('Скорость должна быть от 1 до 500 км/ч', 'danger')
                    return redirect(url_for('post.update', id=id))
                    
                if not (1 <= handling <= 10):
                    flash('Управляемость должна быть от 1 до 10', 'danger')
                    return redirect(url_for('post.update', id=id))
                    
                if not (1 <= durability <= 10):
                    flash('Прочность должна быть от 1 до 10', 'danger')
                    return redirect(url_for('post.update', id=id))
                    
                if not (1 <= fuel_consumption <= 10):
                    flash('Расход топлива должен быть от 1 до 10 л/100км', 'danger')
                    return redirect(url_for('post.update', id=id))
                    
                if not (1 <= seating_capacity <= 8):
                    flash('Количество мест должно быть от 1 до 8', 'danger')
                    return redirect(url_for('post.update', id=id))
                    
            except (ValueError, TypeError):
                flash('Пожалуйста, введите корректные числовые значения', 'danger')
                return redirect(url_for('post.update', id=id))

            post.car_mark = car_mark
            post.description = description
            post.speed = speed
            post.handling = handling
            post.durability = durability
            post.fuel_consumption = fuel_consumption
            post.seating_capacity = seating_capacity
            post.customizations = customizations

            try:
                db.session.commit()
                flash('Публикация успешно обновлена', 'success')
                return redirect(url_for('post.all'))
            except Exception as E:
                db.session.rollback()
                print(str(E))
                flash('Произошла ошибка при обновлении публикации', 'danger')
                return redirect(url_for('post.update', id=id))
        else:
            return render_template('post/update.html', post=post, form=form)
    else:
        abort(403)

@post.route('/post/<int:id>/delete', methods=['POST', 'GET'])
@login_required
def delete(id):
    post = Post.query.get(id)
    if post.seller.id == session['user_id']:
        try:
            db.session.delete(post)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(str(e))
            return str(e)
    else:
        abort(403)

@post.route('/details/<int:id>', methods=['GET', 'POST'])
def details(id):
    post = Post.query.get_or_404(id)
    seller_number = Number.query.filter_by(owner_id=post.seller.id).first()
    
    comments = db.session.query(
        Review.comment,
        Review.date,
        User.login.label('valuer_login')
    ).join(User, Review.valuer_id == User.id).filter(Review.post_id == id).all()

    if request.method == 'POST':
        if 'new_price' in request.form and session.get('user_id') == post.valuer:
            post.price = request.form['new_price']
            db.session.commit()
            flash('Цена успешно обновлена', 'success')
            return redirect(url_for('post.details', id=id))
        
        if 'comment' in request.form and session.get('user_id'):
            comment = Review(
                post_id=id,
                valuer_id=session['user_id'],
                comment=request.form['comment']
            )
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий добавлен', 'success')
            return redirect(url_for('post.details', id=id))

    return render_template('post/car.html', post=post, comments=comments, seller_number=seller_number)