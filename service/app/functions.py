import os
import secrets
from flask import current_app
from faker import Faker
from PIL import Image
import io

fake = Faker()

def save_picture(picture_data):
    if not picture_data:
        return None
        
    
    filename = picture_data.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext not in ['jpg', 'jpeg', 'png']:
        return None
        
    
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture_data.filename)
    picture_fn = random_hex + '.jpg' 
    
    
    image = Image.open(picture_data)
    
    
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    
    
    max_size = (800, 800)
    
    
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    
    upload_path = os.path.join(current_app.root_path, 'static/upload')
    os.makedirs(upload_path, exist_ok=True)
    
    
    picture_path = os.path.join(upload_path, picture_fn)
    image.save(picture_path, 'JPEG', quality=85, optimize=True)
    
    return picture_fn

def generate_random_phone_number():
    return fake.phone_number()
