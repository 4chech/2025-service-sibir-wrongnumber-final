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
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 10:
                flash('Оценка должна быть от 1 до 10', 'danger')
                return redirect(url_for('review.create_review', post_id=post_id))
        except (ValueError, TypeError):
            flash('Оценка должна быть числом от 1 до 10', 'danger')
            return redirect(url_for('review.create_review', post_id=post_id))
        
        if rating and comment:
            review = Review(
                post_id=post_id,
                valuer_id=session['user_id'],
                rating=rating,
                comment=comment
            )
            
            try:
                db.session.add(review)
                db.session.commit()
                flash('Оценка успешно добавлена', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Произошла ошибка при добавлении оценки', 'danger')
                print(str(e))
        
        return redirect(url_for('post.details', id=post_id))
    
    return render_template('review/create.html', post=post)


@review.route('/review/my_reviews', methods = ['GET'])
def my_reviews():
    reviews = db.session.query(
        Review.rating,
        Review.comment,
        Review.date,
        Post.car_mark
    ).join(Post, Review.post_id == Post.id).filter(Review.valuer_id == session['user_id']).all()
    return render_template('review/my_reviews.html', reviews=reviews)

