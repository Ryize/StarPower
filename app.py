"""
Модуль приложения Flask для создания блога.

Данный модуль инициализирует веб-приложение Flask, настраивает связь с базой данных через
SQLAlchemy, управление сессиями пользователей с помощью Flask-Login, выводит уведомления
через Toastr и предоставляет инструменты для отладки приложения с помощью
Flask-DebugToolbar. Также включает настройки для загрузки изображений пользователями.

Атрибуты:
    app (Flask): Объект приложения Flask, представляющий ваше веб-приложение.
    db (SQLAlchemy): Объект для взаимодействия с базой данных.
    manager (LoginManager): Менеджер для управления пользовательскими сессиями и аутентификацией.
    toastr (Toastr): Инструмент для вывода стилизованных уведомлений в интерфейсе пользователя.
    toolbar (DebugToolbarExtension): Панель инструментов для отладки приложения во время разработки.

Константы:
    UPLOAD_FOLDER (str): Путь к директории на сервере, где будут храниться загруженные файлы.
    ALLOWED_EXTENSIONS (set): Набор разрешенных к загрузке типов файлов (изображения).

Конфигурации:
    SECRET_KEY: Секретный ключ для подписи сессии и защиты от CSRF-атак.
    SQLALCHEMY_DATABASE_URI: URI подключения к базе данных, берется из переменных окружения.
    TOASTR_SHOW_METHOD: Метод отображения уведомлений Toastr.
    TOASTR_TIMEOUT: Время отображения уведомлений в миллисекундах.
    UPLOAD_FOLDER: Путь к директории для загрузки файлов.
    MAX_CONTENT_LENGTH: Максимальный размер загружаемого файла в байтах.
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
app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB')

# Инициализация компонентов приложения
db = SQLAlchemy(app)
manager = LoginManager(app)
toastr = Toastr(app)
app.config['TOASTR_SHOW_METHOD'] = 'show'
app.config['TOASTR_TIMEOUT'] = 5000

toolbar = DebugToolbarExtension(app)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024


