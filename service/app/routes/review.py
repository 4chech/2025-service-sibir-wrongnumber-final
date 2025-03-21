from flask import Blueprint, request, redirect, render_template, flash
from flask_login import login_required, current_user

from ..models.review import Rating
from ..extensions import db
from ..models.post import Post

review = Blueprint('review', __name__)

@review.route('/review/<int:post_id>/create_review', methods=['GET', 'POST'])
@login_required
def create_review(post_id):
    post = Post.query.get(post_id)  # Извлекаем пост по его ID
    post_id = post_id
    if post is None:  # Если пост не найден
        flash('Пост не найден', 'error')
        return redirect('/')

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        # Создание объекта отзыва

        review = Rating(rating=rating, comment=comment, valuer_id = current_user.id, post_id=post_id)

        try:
            db.session.add(review)  # Добавляем объект отзыва в сессию
            db.session.commit()  # Подтверждаем изменения
            comment = eval(comment)
            flash(f'Ваш отзыв {comment} был отправлен владельцу, спасибо!')
            return redirect('/')  # Перенаправляем на главную страницу
        except Exception as e:
            db.session.rollback()  # Откатываем изменения в случае ошибки
            print(str(e))
            flash('Вам запрещено оставлять отзывы.',
                  'error')  # Сообщаем об ошибке

    # Передаем объект post в шаблон, чтобы получить доступ к его атрибутам
    return render_template('review/create_review.html', post=post)


@review.route('/review/my_reviews', methods = ['GET'])
def my_reviews():
    reviews = Rating.query.all()  # делаем запрос в базу данных и дёргаем все записи из неё
    return render_template('review/my_reviews.html', reviews=reviews) # передаём reviews в render_template

