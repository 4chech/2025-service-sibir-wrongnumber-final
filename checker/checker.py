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

if len(sys.argv) != 5:
    print(f"\nUsage: {sys.argv[0]} <ip> <port> <login> <flag_id> <flag>\n")
    print(f"Example: {sys.argv[0]} 192.168.1.1 8080 admin goijfdsogijdpfoig c01d4567-e89b-12d3-a456-426600000010\n")
    exit(0)


# service functions

def put_flag(ip, port, login, flag):
    try:
        # Формируем URL для регистрации
        register_url = f"http://{ip}:{port}/user/register"
        
        # Получаем случайную аватарку из папки
        avatars_dir = "images/avatars"
        avatar_files = [f for f in os.listdir(avatars_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        if not avatar_files:
            print("No avatar files found")
            return None
        random_avatar = random.choice(avatar_files)
        avatar_path = os.path.join(avatars_dir, random_avatar)
        
        # Создаем сессию для сохранения cookies
        session = requests.Session()
        
        # Сначала получаем страницу регистрации для получения CSRF токена
        response = session.get(register_url)
        if response.status_code != 200:
            print(f"Failed to get registration page: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # Подготавливаем данные для отправки
        password = "password123"  # Можно сделать случайным
        data = {
            'csrf_token': csrf_token,
            'login': login,
            'flag': flag,  # Номер телефона (флаг)
            'password': password,
            'confirm_password': password
        }
        
        # Открываем файл аватарки
        files = {
            'avatar': ('avatar.jpg', open(avatar_path, 'rb'), 'image/jpeg')
        }
        
        # Отправляем POST запрос на регистрацию
        response = session.post(register_url, data=data, files=files)
        

        # Проверяем результат регистрации
        if response.status_code != 200:
            print(f"Failed to register user: {response.status_code}")
            return None
            
        # Теперь выполняем вход в систему
        login_url = f"http://{ip}:{port}/user/login"
        
        # Получаем страницу входа для получения CSRF токена
        response = session.get(login_url)
        if response.status_code != 200:
            print(f"Failed to get login page: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # Подготавливаем данные для входа
        login_data = {
            'csrf_token': csrf_token,
            'login': login,
            'password': password,
            'remember': True
        }
        
        # Отправляем POST запрос на вход
        response = session.post(login_url, data=login_data)
        
        # Проверяем результат входа
        if response.status_code == 200:
            print(f"Successfully registered and logged in user {login} with flag {flag}")
            return session
        else:
            print(f"Failed to login user: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error during registration/login: {str(e)}")
        return None


def check_flag(ip, port, login, flag, session):
    try:
        # Формируем URL для проверки флага
        url = f"http://{ip}:{port}/api/v1/numbers/checkout/{login}"
        
        # Отправляем GET запрос для получения HTML страницы
        response = session.get(url)
        
        # Проверяем статус ответа
        if response.status_code != 200:
            print(f"Failed to get page: {response.status_code}")
            service_corrupt()
            return False

        # Парсим HTML и ищем флаг
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем флаг на странице (он должен быть виден, так как это наш пользователь)
        if flag in response.text:
            print(f"Flag {flag} found on the page")
            return True
        else:
            print(f"Flag {flag} not found on the page")
            service_corrupt()
            return False
            
    except Exception as e:
        print(f"Error during flag check: {str(e)}")
        service_down()
        return False


def create_post(ip, port, session):
    try:
        # Сначала проверим, что мы авторизованы
        main_page = session.get(f"http://{ip}:{port}/")
        print("\nChecking authorization:")
        print(f"Main page status: {main_page.status_code}")
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

        # Подготавливаем данные формы
        data = {
            'car_mark': 'Test Car',
            'description': 'Test Description',
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
            
            print("\nDebug information:")
            print("1. Request details:")
            print(f"URL: {post_url}")
            print(f"Form data: {data}")
            print(f"File being sent: {random_car}")
            
            # Отправляем POST запрос
            response = session.post(
                post_url,
                data=data,
                files=files,
                allow_redirects=True
            )
        
        print("\n2. Response details:")
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response text: {response.text}")
        
        # Проверяем, есть ли сообщение об ошибке в ответе
        soup = BeautifulSoup(response.text, 'html.parser')
        flash_messages = soup.find_all(class_='alert')
        if flash_messages:
            print("\n3. Flash messages found:")
            for message in flash_messages:
                print(f"Message: {message.text.strip()}")
        
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

def set_price():
    pass

if __name__ == "__main__":
    session = put_flag(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    if not session:
        service_corrupt()
        exit(102)
        
    if not check_flag(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], session):
        service_corrupt()
        exit(102)
        
    if not create_post(sys.argv[1], sys.argv[2], session):
        service_corrupt()
        exit(102)
        
    # Если все операции выполнены успешно
    service_up()
    exit(101)