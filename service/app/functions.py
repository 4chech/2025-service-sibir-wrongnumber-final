import os
import uuid
import secrets
from flask import current_app
from faker import Faker

fake = Faker('en_US')

def save_picture(picture):
    if not picture:
        return None
        
    # Генерируем уникальное имя файла
    _, f_ext = os.path.splitext(picture.filename)
    unique_filename = secrets.token_hex(8) + f_ext
    
    # Получаем и проверяем конфигурацию
    print("Current app config:", current_app.config)
    app_root = current_app.root_path
    print("App root path:", app_root)
    
    # Формируем путь для сохранения
    save_dir = os.path.join(app_root, 'static', 'upload')
    print("Save directory:", save_dir)
    
    # Создаем директорию если её нет
    os.makedirs(save_dir, exist_ok=True)
    
    # Сохраняем файл
    picture_path = os.path.join(save_dir, unique_filename)
    print("Final save path:", picture_path)
    picture.save(picture_path)
    
    return unique_filename

def generate_random_phone_number():
    return fake.phone_number()
