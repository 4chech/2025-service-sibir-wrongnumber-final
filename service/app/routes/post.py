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
    posts = Post.query.order_by(Post.date.desc()).all()
    for post in posts:
        if post.valuer:
            valuer_user = User.query.get(post.valuer)
            if valuer_user:
                # Создаем новый атрибут для хранения логина оценщика
                post.valuer_login = valuer_user.login
            else:
                post.valuer_login = "Неизвестный оценщик"
        else:
            post.valuer_login = "Нет оценщика"
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
        picture = save_picture(form.picture.data)
        user_number = Number.query.filter_by(owner_id=session['user_id']).first()
        
        # Получаем всех пользователей, кроме текущего и админа
        valuers = User.query.filter(
            User.id != session['user_id'],
            User.status != 'admin'
        ).all()

        if not valuers:
            flash("Нет доступных оценщиков для назначения", "danger")
            return redirect(url_for('post.all'))

        # Выбираем случайного оценщика
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
            picture=f'upload/{picture}' if picture else None,
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
            post.car_mark = request.form.get('car_mark')
            post.price = request.form.get('price')
            post.description = request.form.get('description')
            post.speed = request.form.get('speed')
            post.handling = request.form.get('handling')
            post.durability = request.form.get('durability')
            post.fuel_consumption = request.form.get('fuel_consumption')
            post.seating_capacity = request.form.get('seating_capacity')
            post.customizations = request.form.get('customizations')

            try:
                db.session.commit()
                return redirect('/')
            except Exception as E:
                print(str(E))
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

@post.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'python_file' in request.files:
            file = request.files['python_file']
            if file and file.filename.endswith('.py'):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['SERVER_PATH'], filename))
                return f'File {filename} uploaded successfully'
    return render_template('upload.html')
