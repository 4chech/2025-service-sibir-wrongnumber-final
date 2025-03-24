from flask import Blueprint, render_template, request, jsonify, session
from flask_migrate import current
from sqlalchemy.sql.functions import current_user

from ..extensions import db
from ..models.number import Number
from ..models.user import User
from flask_login import current_user


numbers = Blueprint('numbers', __name__)
is_admin = False


@numbers.route('/api/v1/numbers',  methods=['GET'])
def all_numbers():
    numbers = Number.query.order_by(Number.id.desc()).limit(30).all()
    return render_template("/numbers/all_numbers.html", numbers=numbers)


@numbers.route('/api/v1/numbers/checkout/<string:login>',  methods=['GET', 'POST'])
def checkout(login):
    global is_admin
    
    number = Number.query.filter_by(owner_login=login).first()
    
    if not number:
        return jsonify({"error": "Number not found"}), 404

    
    is_admin = session.get('user_status') == 'admin'
    is_owner = session.get('user_id') == number.owner_id
    can_view_secret = is_admin or is_owner

    if request.method == 'GET':
        if request.headers.get("Accept") == 'application/json':
            response_data = {
                "id": number.id,
                "number": number.phone_number,
                "is_admin": is_admin,
                "owner_id": number.owner_id,
                "owner_login": number.owner_login,
            }
            
            
            if can_view_secret:
                response_data["secret"] = number.secret
                
            return jsonify(response_data)
        else:
            return render_template("numbers/one_number.html", 
                                number=number, 
                                show_secret=can_view_secret,
                                secret=number.secret if can_view_secret else None)
            
    elif request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if 'is_admin' in data:
                is_admin = data.get('is_admin')
            
            if is_admin:
                number.phone_number = data.get("number", number.phone_number)
                number.owner_id = data.get("owner_id", number.owner_id)
                number.owner_login = data.get("owner_login", number.owner_login)
                db.session.commit()
                
                return jsonify({
                    "is_admin": is_admin,
                    "id": number.id,
                    "number": number.phone_number,
                    "secret": number.secret,
                    "owner_id": number.owner_id,
                    "owner_login": number.owner_login,
                })
            else:
                return jsonify({"message": "Updated successfully"}), 200

    return jsonify({"error": "Invalid request method"}), 405