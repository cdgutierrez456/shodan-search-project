Shodan Search

Proyecto educativo de ethical hacking en Python. Combina búsquedas en Shodan con verificación automática de credenciales por defecto en instancias DVWA expuestas en internet.

> **Aviso legal:** Este proyecto es exclusivamente para fines educativos y de investigación de seguridad. Usa únicamente en entornos autorizados o en laboratorios controlados (DVWA, TryHackMe, HackTheBox, etc.).

---

## Estructura del proyecto

```
shodan-search-project/
├── pyshodan.py            # Script principal (entry point)
├── shodansearch.py        # Wrapper de la API de Shodan
├── shodan.py              # Mock transparente de la librería shodan (independiente)
├── login_automatization.py # Automatización de login (parcialmente independiente)
└── requirements.txt       # Dependencias
```

---

## Scripts principales

### `pyshodan.py` — Entry point

Script principal que orquesta la búsqueda y verificación de credenciales. Realiza las siguientes acciones:

1. Carga la API key de Shodan desde una variable de entorno (`.env`).
2. Busca instancias DVWA en Shodan con la query `title:dvwa`.
3. Procesa los primeros 5 resultados en paralelo usando `ThreadPoolExecutor`.
4. Para cada resultado, verifica si el host acepta las credenciales por defecto (`admin / password`).
5. Imprime IP, hostname, localización y estado de credenciales.

**Dependencias internas:** `shodansearch.py`, `login_automatization.py`

**Variables de entorno requeridas:**

```env
SHODAN_API_KEY=tu_api_key_aqui
```

**Uso:**

```bash
python pyshodan.py
```

**Ejemplo de salida:**

```
Resultado 0
Direccion IP: 184.72.152.181
Hostname: ['ec2-184-72-152-181.compute-1.amazonaws.com']
Localizacion: {'country_code': 'US', 'city': 'Ashburn', ...}
Credenciales por defecto: True

Tiempo de procesamiento: 3.21s
```

---

### `shodansearch.py` — Wrapper de Shodan

Clase `ShodanSearch` que encapsula el cliente de Shodan y expone un método de búsqueda con manejo de errores.

```python
from shodansearch import ShodanSearch

ssearch = ShodanSearch(api_key="TU_API_KEY")
results = ssearch.search("title:dvwa", page=1)
print(results['matches'])
```

| Método | Descripción |
|--------|-------------|
| `__init__(api_key)` | Inicializa el cliente de Shodan |
| `search(query, page=1)` | Ejecuta una query y retorna los resultados de la página indicada |

---

## Scripts independientes

Estos archivos funcionan de forma autónoma y **no dependen del flujo principal** (`pyshodan.py`).

---

### `shodan.py` — Mock transparente de la API de Shodan

Reemplaza la librería `shodan` real mediante shadowing: al colocarlo en la misma carpeta que tu script, Python lo importa automáticamente en lugar de la librería oficial.

**Propósito:** Permite desarrollar y probar código que usa la API de Shodan sin consumir créditos reales ni necesitar una API key válida.

**Datos incluidos:** 10 instancias DVWA reales (obtenidas de Shodan) distribuidas en varios países (US, Indonesia, Taiwan, Hong Kong, China, Ucrania).

**Uso:**

Basta con tener `shodan.py` en el mismo directorio. No requiere ningún cambio en el código existente:

```python
import shodan  # Importa el mock automáticamente

api = shodan.Shodan("cualquier-string")
results = api.search("title:dvwa")
print(results['total'])  # → número de instancias simuladas
```

**Métodos disponibles:**

| Método | Descripción |
|--------|-------------|
| `Shodan(api_key)` | Constructor (acepta cualquier string como key) |
| `search(query, ...)` | Busca entre los hosts simulados |
| `host(ip)` | Retorna info de un host por IP |
| `info()` | Retorna info de cuenta simulada (100 créditos) |
| `count(query)` | Cuenta resultados de una query |

**Queries soportadas:**
- `title:dvwa` / `dvwa` / `vulnerable` → retorna todos los hosts simulados
- Búsqueda por texto en hostnames, org, product, data

---

### `login_automatization.py` — Automatización de login

Contiene dos funciones de automatización de login completamente independientes entre sí:

---

#### `has_valid_credentials(instance)` — Verificación DVWA

Verifica si una instancia DVWA acepta las credenciales por defecto (`admin / password`) usando `requests`. Maneja el token CSRF necesario para el formulario de login.

```python
from login_automatization import has_valid_credentials

instance = {
    "ip_str": "192.168.1.100",
    "port": 80
}

if has_valid_credentials(instance):
    print("Credenciales por defecto activas")
```

**Flujo interno:**
1. GET a `/login.php` para obtener el token CSRF.
2. POST con `admin / password` + token.
3. Verifica redirección 302 a `index.php` como señal de login exitoso.

> Esta función es usada también por `pyshodan.py`.

---

#### `has_valid_credentials_github()` — Login automático en GitHub

Automatiza el proceso de login en GitHub usando Selenium con Firefox (geckodriver). Útil para demostrar automatización de formularios con autenticación de doble paso o CAPTCHA.

```python
from login_automatization import has_valid_credentials_github

resultado = has_valid_credentials_github()
# True si el login fue exitoso, False si falló
```

**Configuración:** Editar las variables dentro de la función:

```python
user = 'myuser_github'
password = 'mypassword_github'
```

**Requisitos adicionales:** Firefox instalado en el sistema. El geckodriver se descarga automáticamente vía `webdriver-manager`.

---

## Instalación

```bash
# Clonar o entrar al directorio del proyecto
cd shodan-search-project

# Crear entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configurar API key

Crear un archivo `.env` en la raíz del proyecto:

```env
SHODAN_API_KEY=tu_api_key_aqui
```

> Si no tienes API key o quieres probar sin consumir créditos, asegúrate de que `shodan.py` esté en el directorio. El mock se activa automáticamente.

---

## Dependencias principales

| Librería | Uso |
|----------|-----|
| `shodan` | Cliente fake de la API de Shodan |
| `requests` | Peticiones HTTP para verificación de credenciales |
| `selenium` | Automatización de browser (Firefox) |
| `webdriver-manager` | Descarga automática de geckodriver |
| `python-dotenv` | Carga de variables de entorno desde `.env` |

---

## Diagrama de flujo

```
pyshodan.py (main)
    │
    ├── shodansearch.py
    │       └── shodan (librería real o mock shodan.py)
    │
    └── login_automatization.py
            └── has_valid_credentials()

login_automatization.py (independiente)
    └── has_valid_credentials_github()

shodan.py (independiente)
    └── Mock de la API de Shodan
```
