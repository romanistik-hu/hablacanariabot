# HablaCanariaBot

Bot de Telegram para el proyecto "Habla Canaria", desarrollado en Python. Este bot gestiona la recolección de datos de participantes individuales y grupales, interactuando con una base de datos MongoDB.

## Requisitos Previos

- **Python 3.8+**
- **MongoDB** (Local o en clúster)
- **Token de Bot de Telegram** (Obtenido via @BotFather)

## Instalación

1.  Clonar el repositorio:
    ```bash
    git clone https://github.com/johnatanebonilla/hablacanariabot.git
    cd hablacanariabot
    ```

2.  (Opcional pero recomendado) Crear un entorno virtual:
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate
    ```

3.  Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Configuración

1.  Copiar el archivo de ejemplo de variables de entorno:
    ```bash
    cp .env.example .env
    # O en Windows:
    copy .env.example .env
    ```

2.  Editar el archivo `.env` con tus credenciales:
    ```ini
    TELEGRAM_TOKEN=tu_token_de_telegram
    MONGO_USER=tu_usuario_mongo
    MONGO_PASSWORD=tu_contraseña_mongo
    MONGO_HOST=localhost
    MONGO_PORT=27017
    MONGO_DB=tele_db
    ```

## Base de Datos (MongoDB)

El bot utiliza una base de datos MongoDB llamada por defecto `tele_db`.
Si estás usando MongoDB localmente, asegúrate de tener creado el usuario con permisos de lectura y escritura sobre la base de datos `tele_db`, o utiliza un usuario administrador.

El script `forms.py` gestiona la conexión. Las colecciones se crean automáticamente cuando se insertan datos.

### Estructura de Colecciones Principales
- `participante_individual`: Datos de registro individual.
- `tareas`: Tareas asignadas/realizadas.
- `respuestas`: Respuestas a los cuestionarios.

## Ejecución

Para iniciar el bot:

```bash
python bot.py
```

El bot debería iniciar sesión y comenzar a escuchar mensajes. Los logs se guardan en `errors.log` y en la consola.
