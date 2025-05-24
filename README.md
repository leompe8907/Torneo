Django API - Backend del Proyecto
Este es un proyecto backend desarrollado con Django 5 y Django REST Framework. Soporta autenticación con JWT, conexión a base de datos MySQL y configuración para CORS, ideal para integrarse con un frontend moderno.

⚙️ Tecnologías
Python

Django 5

Django REST Framework

SimpleJWT (para autenticación)

MySQL (con mysqlclient)

CORS Headers

📦 Requisitos
Python 3.10+

MySQL Server

pip

🔧 Instalación
Clona este repositorio:

bash
Copiar
Editar
git clone https://github.com/leompe8907/Torneo.git
cd nombre-del-repo
Crea y activa un entorno virtual:

bash
Copiar
Editar
python -m venv env
source env/bin/activate
Windows: env\\Scripts\\activate
Instala las dependencias:

bash
Copiar
Editar
pip install -r requirements.txt
Configura la base de datos en mysite/settings.py.

Aplica migraciones:

bash
Copiar
Editar
python manage.py migrate
Ejecuta el servidor:

bash
Copiar
Editar
python manage.py runserver
🧪 Pruebas
Puedes correr los tests definidos con:

bash
Copiar
Editar
python manage.py test
🌐 API
Esta aplicación expone una API REST. Requiere autenticación JWT para la mayoría de los endpoints. Puedes obtener un token en el endpoint /api/token/.

🛡️ Seguridad
Manejo de tokens JWT.
Soporte CORS para integración con frontends externos.