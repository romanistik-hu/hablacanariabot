# HablaCanariaBot

This bot was developed by Dr. Johnatan E. Bonilla as part of project A09 "On the interplay between register and socio-geographic variation in Canarian Spanish" within the Collaborative Research Centre 1412 "REGISTER" (Register: Language Users' Knowledge of Situational-Functional Variation), led by Prof. Dr. Miriam Bouzouita at Humboldt-Universität zu Berlin.

Telegram bot for the "Habla Canaria" project, developed in Python. This bot manages data collection from individual and group participants, interacting with a MongoDB database.

## Prerequisites

- **Python 3.8+**
- **MongoDB** (Local or Cluster)
- **Telegram Bot Token** (Obtained via @BotFather)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/romanistik-hu/hablacanariabot.git
    cd hablacanariabot
    ```

2.  (Optional but recommended) Create a virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On Linux/Mac:
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy the example environment variables file:
    ```bash
    cp .env.example .env
    # Or on Windows:
    copy .env.example .env
    ```

2.  Edit the `.env` file with your credentials:
    ```ini
    TELEGRAM_TOKEN=your_telegram_token
    MONGO_USER=your_mongo_user
    MONGO_PASSWORD=your_mongo_password
    MONGO_HOST=localhost
    MONGO_PORT=27017
    MONGO_DB=tele_db
    ```

## Database (MongoDB)

The bot uses a MongoDB database named `tele_db` by default.
If you are using MongoDB locally, make sure you have created the user with read/write permissions on the `tele_db` database, or use an administrator user.

The `forms.py` script manages the connection. Collections are created automatically when data is inserted.

### Main Collection Structure
- `participante_individual`: Individual registration data.
- `tareas`: Assigned/completed tasks.
- `respuestas`: Questionnaire responses.
- `participantes_pareja`: Pair registration data.
- `consentimientos`: Consent forms.

## Usage

To start the bot:

```bash
python bot.py
```

The bot should log in and start listening for messages. Logs are saved in `errors.log` and displayed in the console.
