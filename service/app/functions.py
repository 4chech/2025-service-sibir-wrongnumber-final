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
        
    # Проверяем расширение файла
    filename = picture_data.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext not in ['jpg', 'jpeg', 'png']:
        return None
        
    # Генерируем уникальное имя файла
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture_data.filename)
    picture_fn = random_hex + '.jpg'  # Всегда сохраняем в jpg для экономии места
    
    # Открываем изображение с помощью Pillow
    image = Image.open(picture_data)
    
    # Конвертируем в RGB (если изображение в RGBA)
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    
    # Определяем максимальный размер
    max_size = (800, 800)
    
    # Сжимаем изображение с сохранением пропорций
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Создаем директорию, если её нет
    upload_path = os.path.join(current_app.root_path, 'static/upload')
    os.makedirs(upload_path, exist_ok=True)
    
    # Сохраняем сжатое изображение
    picture_path = os.path.join(upload_path, picture_fn)
    image.save(picture_path, 'JPEG', quality=85, optimize=True)
    
    return picture_fn

def generate_random_phone_number():
    return fake.phone_number()
