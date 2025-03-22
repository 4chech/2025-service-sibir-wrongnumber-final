from flask import Blueprint, request, redirect, render_template, flash, session, url_for
from flask_login import login_required, current_user

from ..models.post import Post
from ..models.user import User
from ..models.review import Review
from ..extensions import db

review = Blueprint('review', __name__)

@review.route('/review/create/<int:post_id>', methods=['GET', 'POST'])
def create_review(post_id):
    if not session.get('user_id'):
        return redirect(url_for('user.login'))

    post = Post.query.get_or_404(post_id)
    
    if session['user_id'] != post.valuer:
        flash('У вас нет прав на оценку этого автомобиля', 'danger')
        return redirect(url_for('post.details', id=post_id))

    if request.method == 'POST':
        comment = request.form.get('comment')
        
        if comment:
            review = Review(
                post_id=post_id,
                valuer_id=session['user_id'],
                comment=comment
            )
            
            try:
                db.session.add(review)
                db.session.commit()
                flash('Отзыв успешно добавлен', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Произошла ошибка при добавлении отзыва', 'danger')
                print(str(e))
        
        return redirect(url_for('post.details', id=post_id))
    
    return render_template('review/create.html', post=post)


@review.route('/review/my_reviews', methods = ['GET'])
def my_reviews():
    reviews = Review.query.all()  # делаем запрос в базу данных и дёргаем все записи из неё
    return render_template('review/my_reviews.html', reviews=reviews) # передаём reviews в render_template

