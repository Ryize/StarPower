"""
Модуль приложения Flask для прогнозирования гороскопов.

Этот модуль отвечает за инициализацию основного объекта Flask приложения, его конфигурацию,
а также подключение и настройку различных расширений Flask. Включает в себя настройку подключения к базе данных,
управление пользовательскими сессиями, отображение всплывающих уведомлений и инструменты для отладки.

Константы:
    UPLOAD_FOLDER (str): Путь к директории для загружаемых файлов.
    ALLOWED_EXTENSIONS (set[str]): Набор разрешенных типов файлов для загрузки.

Конфигурации:
    SECRET_KEY (str): Секретный ключ для поддержания безопасности сессий и cookies.
    SQLALCHEMY_DATABASE_URI (str): URI для подключения к базе данных.
    TOASTR_SHOW_METHOD (str): Метод отображения всплывающих уведомлений Toastr.
    TOASTR_TIMEOUT (int): Время отображения уведомлений в миллисекундах.
    UPLOAD_FOLDER (str): Конфигурация директории для загружаемых файлов.
    MAX_CONTENT_LENGTH (int): Максимальный размер загружаемого файла в байтах.

Атрибуты:
    app (Flask): Экземпляр приложения Flask.
    db (SQLAlchemy): Объект для работы с базой данных через ORM.
    manager (LoginManager): Менеджер для управления пользовательскими сессиями.
    toastr (Toastr): Система уведомлений для фронтенда.
"""

import uuid
import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_toastr import Toastr


# Инициализация объекта приложения Flask
app = Flask(__name__)

# Конфигурация приложения
app.config["SECRET_KEY"] = str(uuid.uuid4())
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB")

# Инициализация расширений Flask
db = SQLAlchemy(app)
manager = LoginManager(app)
toastr = Toastr(app)
app.config["TOASTR_SHOW_METHOD"] = "show"
app.config["TOASTR_TIMEOUT"] = 4000

toolbar = DebugToolbarExtension(app)

# Конфигурация загрузки файлов
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif",}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024
