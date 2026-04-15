import requests
import re
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import FirefoxOptions, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

def has_valid_credentials_github():
    """Realiza login en github de manera automatica con selenium"""
    # Incializamos el driver de firefox
    service = Service(GeckoDriverManager().install())
    options = FirefoxOptions()
    driver = Firefox(service=service, options=options)

    # Obtenemos la pagina de login de GitHub
    driver.get('https://github.com/login')

    # Buscamos el campo login y password
    user = 'myuser_github'
    password = 'mypassword_github'


    password_html_element = driver.find_element(By.ID, 'password')

    driver.find_element(By.ID, 'login_field').send_keys(user)

    # Eliminando atributo disabled en input password para poder interacturar
    driver.execute_script('arguments[0].removeAttribute("disabled")', password_html_element)
    password_html_element.send_keys(password)

    # Pulsamos sobre el boton enviar
    driver.find_element(By.NAME, 'commit').click()

    # Comprobamos si el login ha sido exitoso
    WebDriverWait(driver=driver, timeout=10).until(
        lambda x: x.execute_script('return document.readyState == "complete"')
    )

    err_msg = 'Incorrect username or password'

    errors = driver.find_elements(By.CLASS_NAME, 'js-flash-alert')

    if any(err_msg in e.text for e in errors):
        print("[!] El login no ha tenido exito.")
        driver.close()
        return False
    else:
        print('[+] El login ha tenido exito')
        driver.close()
        return True


def has_valid_credentials(instance):
    """Verificar si una instancia de DVWA tiene credenciales por defecto."""
    sess = requests.Session()
    proto = 'https' if 'ssl' in instance else 'http'
    login_page = f'{proto}://{instance["ip_str"]}:{instance["port"]}/login.php'

    try:
        response = sess.get(login_page, verify=False) # No verifica el certificado SSL del servidor
    except requests.exceptions.ConnectionError as e:
        print(f'!!! Error al intentar conectarse al host {instance['ip_str']}: {e}')
        return False
    if response.status_code != 200:
        print(f'!!! Error en la respuesta del servidor. Respuesta: {response.status_code}')
        return False

    # Obtener el token CSRF
    try:
        token = re.search(r"user_token' value='([0-9a-f]+)'", response.text).group(1) # type: ignore
    except Exception as e:
        print(f'!!! Error al obtener el token CSRF: {e}')
        return False

    response = sess.post(
        login_page,
        f"username=admin&password=password&user_token={token}&Login=Login",
        allow_redirects=False,
        verify=False,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    # Si la respuesta es una redireccion a index.php, entonces el login es exitoso
    if response.status_code == 302 and response.headers['Location'] == 'index.php':
        return True
    else:
        return False