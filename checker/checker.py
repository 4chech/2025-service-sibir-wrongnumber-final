# import
import sys
import requests
import random
import os
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder


# service status



def service_up():
    print("[service is worked] - 101")
    exit(101)

def service_corrupt():
    print("[service is not worked] - 102")
    exit(102)

def service_muble():
    print("[service is muble] - 103")
    exit(103)

def service_down():
    print("[service is down] - 104")
    exit(104)

if len(sys.argv) != 4:
    print(f"\nUsage: {sys.argv[0]} <ip> <put/check> <flag_id> <flag>\n")
    print(f"Example: {sys.argv[0]} 192.168.1.1 put flag_id c01d4567-e89b-12d3-a456-426600000010\n")
    exit(0)


# service functions

def get_random_login():
    try:
        with open('names/logins.txt', 'r') as f:
            logins = f.readlines()
            return random.choice(logins).strip()
    except Exception as e:
        print(f"Error reading logins file: {str(e)}")
        return None

def put_flag(ip, port, flag_id, flag):
    try:
        # Создаем сессию для сохранения cookies
        session = requests.Session()
        
        # Регистрируем пользователя через JSON API
        register_url = f"http://{ip}:{port}/user/register"
        register_data = {
            "login": flag_id,  # Используем flag_id как логин
            "password": "password123",
            "flag": flag,
            "status": "user"
        }
        
        response = session.post(
            register_url,
            json=register_data
        )
        
        if response.status_code != 200:
            print(f"Failed to register user: {response.status_code}")
            return None
            
        # Выполняем вход
        login_url = f"http://{ip}:{port}/user/login"
        login_data = {
            "login": flag_id,  # Используем flag_id как логин
            "password": "password123"
        }
        
        response = session.post(login_url, data=login_data)
        
        if response.status_code == 200 or response.status_code == 302:
            print(f"Successfully registered and logged in user {flag_id} with flag {flag}")
            return session
        else:
            print(f"Failed to login user: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error during registration/login: {str(e)}")
        return None


def check_flag(ip, port, flag_id, flag, session):
    try:
        # Получаем данные пользователя по flag_id (который теперь является логином)
        user_data = session.get(f"http://{ip}:{port}/api/v1/numbers/checkout/{flag_id}")
        
        if user_data.status_code != 200:
            print(f"Failed to get user data: {user_data.status_code}")
            service_corrupt()
            return False

        # Проверяем наличие флага в ответе
        if flag in user_data.text:
            print(f"Flag {flag} found")
            return True
        else:
            print(f"Flag {flag} not found")
            service_corrupt()
            return False
            
    except Exception as e:
        print(f"Error during flag check: {str(e)}")
        service_down()
        return False


def get_random_car_name():
    try:
        with open('names/cars.txt', 'r') as f:
            cars = f.readlines()
            return random.choice(cars).strip()
    except Exception as e:
        print(f"Error reading cars file: {str(e)}")
        return "Test Car"

def get_random_description():
    try:
        with open('names/description.txt', 'r', encoding='utf-8') as f:
            # Читаем весь файл и разделяем по пустым строкам
            content = f.read()
            # Разделяем по двойному переносу строки и фильтруем пустые строки
            descriptions = [desc.strip() for desc in content.split('\n\n') if desc.strip()]
            if not descriptions:
                print("No descriptions found in file")
                return "Test Description"
            return random.choice(descriptions)
    except Exception as e:
        print(f"Error reading description file: {str(e)}")
        return "Test Description"

def create_post(ip, port, session):
    try:
        # Проверяем авторизацию через главную страницу
        main_page = session.get(f"http://{ip}:{port}/")
        if "Выйти" not in main_page.text:
            print("Not logged in - no 'Выйти' button found")
            return False

        post_url = f"http://{ip}:{port}/post/create"

        # Проверяем наличие директории с картинками
        if not os.path.exists("images/cars"):
            print("Directory images/cars not found")
            return False

        car_files = [f for f in os.listdir("images/cars") if f.endswith(('.jpg', '.png', '.jpeg'))]
        if not car_files:
            print("No car images found")
            return False

        random_car = random.choice(car_files)
        car_path = os.path.join("images/cars", random_car)

        # Получаем случайное название машины и описание
        car_name = get_random_car_name()
        description = get_random_description()
        
        print("\nSelected description:")
        print(description)

        # Подготавливаем данные формы
        data = {
            'car_mark': car_name,
            'description': description,
            'speed': '100',
            'handling': '10',
            'durability': '10',
            'fuel_consumption': '10',
            'seating_capacity': '2',
            'customizations': 'Test Customizations'
        }

        # Открываем файл картинки
        with open(car_path, 'rb') as car_file:
            files = {
                'picture': (random_car, car_file, 'image/jpeg')
            }
            
            # Отправляем POST запрос
            response = session.post(
                post_url,
                data=data,
                files=files,
                allow_redirects=True
            )
        
        if response.status_code == 200 or response.status_code == 302:
            if "У вас нет прав на создание публикаций" in response.text:
                print("\nError: No permissions to create posts")
                return False
            print("Successfully created post")
            return True
        else:
            print(f"\nFailed to create post: {response.status_code}")
            return False

    except Exception as e:
        print(f"\nError during create post: {str(e)}")
        service_down()
        return False

def create_comment():
    pass

if command == "put":
    put_flag(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    check_flag(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    create_post(sys.argv[1], sys.argv[2], sys.argv[3])
    service_up()

if command == "check":
    check_flag(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    service_up()

