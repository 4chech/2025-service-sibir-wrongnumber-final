import os
import secrets
from flask import current_app
from faker import Faker

fake = Faker('en_US')

def save_picture(picture):
    if not picture:
        return None
        
    # Генерируем уникальное имя файла
    _, f_ext = os.path.splitext(picture.filename)
    unique_filename = secrets.token_hex(16) + f_ext
    
    # Формируем путь для сохранения
    save_dir = os.path.join(current_app.root_path, 'static', 'upload')
    
    # Создаем директорию если её нет
    os.makedirs(save_dir, exist_ok=True)
    
    # Сохраняем файл
    picture_path = os.path.join(save_dir, unique_filename)
    picture.save(picture_path)
    
    return unique_filename

def generate_random_phone_number():
    return fake.phone_number()
