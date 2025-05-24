# Django API - Backend del Proyecto

Este es el backend de un proyecto desarrollado con **Django 5** y **Django REST Framework**. Incluye **autenticación JWT**, conexión a **bases de datos MySQL** y configuración **CORS**, lo que lo hace perfecto para integrarse con cualquier frontend moderno.

---

## ⚙️ Tecnologías Utilizadas

* **Python**
* **Django 5**
* **Django REST Framework**
* **SimpleJWT** (para autenticación segura)
* **MySQL** (a través de `mysqlclient`)
* **CORS Headers**

---

## 📦 Requisitos Previos

Asegúrate de tener instalado lo siguiente:

* **Python 3.10+**
* **Servidor MySQL** en ejecución
* **pip** (gestor de paquetes de Python)

---

## 🔧 Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/leompe8907/Torneo.git
    cd Torneo
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv env
    # En Linux/macOS:
    source env/bin/activate
    # En Windows:
    .\env\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplica las migraciones de la base de datos:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Ejecuta el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

---