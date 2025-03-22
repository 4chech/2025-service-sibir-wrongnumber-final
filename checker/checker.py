# import
import sys
import requests
import random
import os
import hashlib
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

# service functions

def get_random_login():
    try:
        with open('names/logins.txt', 'r') as f:
            logins = f.readlines()
            return random.choice(logins).strip()
    except Exception as e:
        print(f"Error reading logins file: {str(e)}")
        return None

def generate_password(flag_id):
    salt = "cyberpunk2077"  # фиксированная соль
    return hashlib.md5((flag_id + salt).encode()).hexdigest()

def put_flag(ip, port, flag_id, flag):
    try:
        session = requests.Session()
        password = generate_password(flag_id)
        
        print(f"\n[DEBUG] Login: {flag_id}")
        print(f"[DEBUG] Password: {password}")
        
        # Проверяем наличие директории с аватарками
        if not os.path.exists("images/avatars"):
            print("[ERROR] Directory images/avatars not found")
            service_corrupt()
            return None

        avatar_files = [f for f in os.listdir("images/avatars") if f.endswith(('.jpg', '.png', '.jpeg'))]
        if not avatar_files:
            print("[ERROR] No avatar images found")
            service_corrupt()
            return None

        random_avatar = random.choice(avatar_files)
        avatar_path = os.path.join("images/avatars", random_avatar)
        
        # Регистрация пользователя через форму
        register_url = f"http://{ip}:{port}/register"
        print(f"[DEBUG] Register URL: {register_url}")
        
        # Открываем файл аватарки и готовим данные формы
        with open(avatar_path, 'rb') as avatar_file:
            files = {
                'avatar': (random_avatar, avatar_file, 'image/jpeg')
            }
            data = {
                'login': flag_id,
                'password': password,
                'confirm_password': password,
                'flag': flag
            }
            
            print("[DEBUG] Sending registration request...")
            response = session.post(
                register_url,
                data=data,
                files=files
            )
            print(f"[DEBUG] Register response: {response.status_code}")
            print(f"[DEBUG] Register content: {response.text[:500]}...")
            
            # Проверяем, есть ли в ответе сообщение об ошибке
            if "Этот логин уже занят" in response.text:
                print("[ERROR] Login already exists")
                service_corrupt()
                return None
            if "Пароли не совпадают" in response.text:
                print("[ERROR] Passwords do not match")
                service_corrupt()
                return None
            if "Произошла ошибка при регистрации" in response.text:
                print("[ERROR] Registration error occurred")
                service_corrupt()
                return None
        
        if response.status_code != 200 and response.status_code != 302:
            print("[ERROR] Registration failed")
            service_corrupt()
            return None
            
        # Логин через форму
        login_url = f"http://{ip}:{port}/login"
        print(f"[DEBUG] Login URL: {login_url}")
        
        login_data = {
            'login': flag_id,
            'password': password
        }
        print(f"[DEBUG] Login data: {login_data}")
        
        print("[DEBUG] Sending login request...")
        response = session.post(login_url, data=login_data)
        print(f"[DEBUG] Login response: {response.status_code}")
        print(f"[DEBUG] Login content: {response.text[:500]}...")
        
        if response.status_code != 200 and response.status_code != 302:
            print("[ERROR] Login failed")
            service_corrupt()
            return None

        # Проверяем успешность логина
        main_page = session.get(f"http://{ip}:{port}/")
        print(f"[DEBUG] Main page response: {main_page.status_code}")
        print(f"[DEBUG] Main page content: {main_page.text[:500]}...")
        
        if "Выйти" not in main_page.text:
            print("[ERROR] Login verification failed")
            service_corrupt()
            return None

        # Проверка флага на странице информации о номере
        check_url = f"http://{ip}:{port}/api/v1/numbers/checkout/{flag_id}"
        print(f"[DEBUG] Check flag URL: {check_url}")
        
        check_response = session.get(check_url)
        print(f"[DEBUG] Check flag response: {check_response.status_code}")
        print(f"[DEBUG] Check flag content: {check_response.text[:500]}...")
        
        if check_response.status_code != 200:
            print("[ERROR] Failed to get flag page")
            service_corrupt()
            return None

        # Парсим HTML страницу для поиска флага
        soup = BeautifulSoup(check_response.text, 'html.parser')
        # Ищем span с флагом после strong с текстом "Флаг:"
        flag_label = soup.find('strong', string='Флаг:')
        if not flag_label:
            print("[ERROR] Flag label not found on page")
            service_corrupt()
            return None
            
        flag_span = flag_label.find_next('span')
        if not flag_span or flag not in flag_span.text:
            print("[ERROR] Flag not found on page")
            service_corrupt()
            return None

        print("[SUCCESS] Registration and flag verification completed")
        return session

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        print(f"[ERROR] Exception type: {type(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        service_down()
        return None


def check_flag(ip, port, flag_id, flag):
    try:
        session = requests.Session()
        password = generate_password(flag_id)

        print(f"\n[DEBUG] Login: {flag_id}")
        print(f"[DEBUG] Password: {password}")

        # Логин через форму
        login_url = f"http://{ip}:{port}/login"
        login_data = {
            'login': flag_id,
            'password': password
        }
        
        response = session.post(login_url, data=login_data)
        print(f"[DEBUG] Login response: {response.status_code}")
        print(f"[DEBUG] Login content: {response.text[:500]}...")
        
        if response.status_code != 200 and response.status_code != 302:
            print("[ERROR] Login failed")
            service_corrupt()
            return False

        # Проверяем успешность логина
        main_page = session.get(f"http://{ip}:{port}/")
        if "Выйти" not in main_page.text:
            print("[ERROR] Login verification failed")
            service_corrupt()
            return False

        # Проверка флага на странице информации о номере
        check_url = f"http://{ip}:{port}/api/v1/numbers/checkout/{flag_id}"
        api_response = session.get(check_url)
        print(f"[DEBUG] Check flag response: {api_response.status_code}")
        print(f"[DEBUG] Check flag content: {api_response.text[:500]}...")
        
        if api_response.status_code != 200:
            print("[ERROR] Failed to get flag page")
            service_corrupt()
            return False

        # Парсим HTML страницу для поиска флага
        soup = BeautifulSoup(api_response.text, 'html.parser')
        # Ищем span с флагом после strong с текстом "Флаг:"
        flag_label = soup.find('strong', string='Флаг:')
        if not flag_label:
            print("[ERROR] Flag label not found on page")
            service_corrupt()
            return False
            
        flag_span = flag_label.find_next('span')
        if not flag_span or flag not in flag_span.text:
            print("[ERROR] Flag not found on page")
            service_corrupt()
            return False

        # Проверка видимости flag_id на странице всех постов
        posts_response = session.get(f"http://{ip}:{port}/")
        print(f"[DEBUG] Posts page response: {posts_response.status_code}")
        
        if posts_response.status_code != 200:
            print("[ERROR] Failed to get posts page")
            service_corrupt()
            return False

        if flag_id not in posts_response.text:
            print("[ERROR] Flag ID not visible on posts page")
            service_corrupt()
            return False

        # Выход из системы
        logout_response = session.get(f"http://{ip}:{port}/logout")
        print(f"[DEBUG] Logout response: {logout_response.status_code}")
        
        if logout_response.status_code != 200 and logout_response.status_code != 302:
            print("[ERROR] Logout failed")
            service_corrupt()
            return False

        print("[SUCCESS] Flag check completed successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
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

def logout(ip, port, session):
    try:
        logout_url = f"http://{ip}:{port}/logout"
        print(f"\n[DEBUG] Logging out:")
        print(f"[DEBUG] Logout URL: {logout_url}")
        
        print("[DEBUG] Sending logout request...")
        logout_response = session.get(logout_url)
        print(f"[DEBUG] Response status code: {logout_response.status_code}")
        
        if logout_response.status_code != 200 and logout_response.status_code != 302:
            print("[ERROR] Failed to logout")
            print(f"[ERROR] Response content: {logout_response.text}")
            service_corrupt()
            return False
        return True
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        service_down()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(f"\nUsage: {sys.argv[0]} <ip> <port> <method> <flag_id> <flag>\n")
        print(f"Example: {sys.argv[0]} 127.0.0.1 8080 put flag_id flag_value\n")
        exit(0)

    ip = sys.argv[1]
    port = sys.argv[2]
    method = sys.argv[3]
    flag_id = sys.argv[4]
    flag = sys.argv[5]

    try:
        if method == "put":
            session = put_flag(ip, port, flag_id, flag)
            if session is None:
                service_corrupt()
            if not create_post(ip, port, session):
                service_corrupt()
            if not logout(ip, port, session):
                service_corrupt()
            service_up()
        
        elif method == "check":
            if check_flag(ip, port, flag_id, flag):
                service_up()
            else:
                service_corrupt()
        
        else:
            print(f"Unknown method: {method}")
            exit(1)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        service_down()