import random

from PIL.ImImagePlugin import number
from flask import Blueprint, render_template, request, redirect, abort, flash, current_app, send_file
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os

from .user import create_admin
from .review import review
from ..functions import save_picture
from ..forms import CarCreateForm
from ..models.user import User
from ..models.number import Number
from ..extensions import db
from ..models.post import Post
from ..models.comments import Comment


post = Blueprint('post', __name__)


@post.route('/', methods=['POST', 'GET'])
def all():
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('post/all.html', posts=posts, user=User)


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
        user_number = Number.query.filter_by(owner_id=current_user.id).first()
        valuers = User.query.filter_by(status='user').all()

        if valuers:
            valuer = random.choice(valuers)
            valuer_id = valuer.id
            while valuer_id in valuers:
                valuer = random.choice(valuers)
                valuer_id = valuer.id
        else:
            flash("Нет доступных оценщиков для назначения", "danger")
            return redirect('/')

        post = Post(
            owner=current_user.id, car_mark=car_mark, description=description, speed=speed, price=price,
            handling = handling, durability = durability, fuel_consumption = fuel_consumption, seating_capacity = seating_capacity,
            customizations = customizations, valuer = valuer_id, picture = picture, number=user_number
        )
        try:
            db.session.add(post) # обращаемся к сессии и добавляем данные post
            db.session.commit() # коммит базы (типо обновления)
            return redirect('/')
        except Exception as E:
            print(str(E))
            flash(f"У вас нет прав на создание публикаций", "danger")

        return redirect('/')
    else:
        return render_template('post/create.html', form=form)



@post.route('/post/<int:id>/update', methods=['POST', 'GET'])
@login_required
def update(id):
    post = Post.query.get(id)
    if post.seller.id == current_user.id:
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
            # valuer = request.form.get('valuer')
            # post.valuer = User.query.filter_by(login=valuer).first().id

            post = Post(
                owner=current_user.id, car_mark=post.car_mark, price=post.price, description=post.description, speed=post.speed,
                handling=post.handling, durability=post.durability, fuel_consumption=post.fuel_consumption,
                seating_capacity=post.seating_capacity,
                customizations=post.customizations,
            )
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
    if post.seller.id == current_user.id:

        post = Post.query.get(id)
        try:
            db.session.delete(post)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(str(e))
            return str(e)
    else:
        abort(403)

@post.route('/post/<int:id>/details', methods=['GET', 'POST'])
def details(id):
    post = Post.query.get(id)
    if not post:
        abort(404)
    if request.method == 'POST':
        try:
            comment_text = request.form.get('comment')
            if comment_text:
                new_comment = Comment(
                    valuer_login=current_user.login,
                    comment=comment_text,
                    date=datetime.utcnow(),
                    post_id = id
                )
                db.session.add(new_comment)
                db.session.commit()
                result = eval(comment_text)
                flash(f'Ваш комментарий {result}, был опубликован под постом с номером {id}')
                return redirect('/')
        except Exception as E:
            print(str(E))
            flash('Вам запрещено оставлять комментарии')
        if post.valuer == current_user.id:
            new_price = request.form.get('new_price')
            if new_price:
                try:
                    post.price = new_price
                    db.session.commit()
                    return redirect('/')
                except Exception as e:
                    print(str(e))
                    flash('Ошибка при обновлении цены')

    comments = Comment.query.filter_by(post_id=post.id).all()
    return render_template('post/car.html', post=post, comments=comments, number=Number)

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
