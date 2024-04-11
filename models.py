"""
Модуль моделей приложения Flask для прогнозирования гороскопов.

Этот модуль отвечает за определение моделей данных, используемых в приложении,
включая пользователей, гороскопы, натальные карты и базовые модели. Включает в
себя методы для управления данными, такие как создание, сохранение и
извлечение записей из базы данных, а также проверка входных данных новых
пользователей.

Классы:
    BaseModel: Базовый класс модели, предоставляющий методы сохранения и
    создания экземпляров модели.
    User: Модель пользователя, содержащая информацию о пользователе, включая
    логин, электронную почту и пароль.
    UserNatalChart: Модель натальной карты пользователя.
    Horoscope: Модель гороскопа, содержащая информацию о прогнозах для
    различных периодов и знаков зодиака.
    DataAccess: Класс для управления доступом к данным, включающий методы для
    работы с пользовательскими данными, гороскопами и натальными картами.

Функции:
    load_user(user_id): Функция для загрузки пользователя по его
    идентификатору, используется flask_login для управления пользовательскими
    сессиями.

Примеры использования:
    # Создание нового пользователя
    new_user = User.create(login='exampleUser', email='user@example.com',
    password='securePassword')

    # Получение гороскопа для определенного знака зодиака и периода
    horoscope = DataAccess().get_horoscope(period='today', date='2023-04-01',
                                           zodiac_sign='Aries')

Зависимости:
    Модуль зависит от Flask, Flask-Login, Flask-SQLAlchemy для работы с
    приложением, управления сессиями и взаимодействия с базой данных.
    Также используется Werkzeug для безопасной работы с паролями и регулярные
    выражения для проверки ввода пользователя.
"""

import re
from datetime import datetime, timezone

from flask import flash
from flask_login import UserMixin, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from zodiac_sign import get_zodiac_sign

from app import app, db, manager


class BaseModel:
    """
    Базовый класс модели для всех моделей данных в приложении.

    Атрибуты:
        id (int): Уникальный идентификатор для каждой записи, который
                  автоматически генерируется базой данных при создании новой
                  записи.
        created_at (datetime): Дата и время создания записи, автоматически
                               устанавливается в момент создания новой записи.

    Методы:
        save(self) -> None:
            Сохраняет текущий экземпляр модели в базе данных. Если объект уже
            существует, он будет обновлен, в противном случае — создан новый.

        create(cls, *args, **kwargs) -> 'BaseModel':
            Классовый метод для создания и сохранения нового экземпляра модели
            в базе данных. Принимает те же параметры, что и конструктор класса.

    Пример использования:
        Наследуя этот класс, можно создать модель пользователя следующим
        образом:
        class User(BaseModel):
            name = db.Column(db.String(50), nullable=False)
            # другие поля...

        Создание и сохранение нового пользователя:
        user = User.create(name='John Doe')
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc))

    def save(self) -> None:
        """
        Добавляет текущий объект в сессию базы данных и сохраняет его.
        Этот метод используется как для добавления новых объектов, так и для
        обновления существующих.
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def create(cls, *args, **kwargs) -> 'BaseModel':
        """
        Создает новый экземпляр класса с заданными аргументами и сохраняет его
        в базе данных.

        Параметры:
            *args: Позиционные аргументы, передаваемые конструктору класса.
            **kwargs: Именованные аргументы, передаваемые конструктору класса.

        Возвращает:
            Экземпляр класса, производного от BaseModel, представляющий
            новосозданную запись в базе данных.
        """
        new_obj = cls(*args, **kwargs)
        new_obj.save()
        return new_obj


class User(db.Model, BaseModel, UserMixin):
    """
    Модель пользователя.

    Атрибуты:
        login (str): Логин пользователя. Уникальный и обязательный.
        email (str): Электронная почта пользователя. Уникальная и обязательная.
        password (str): Хэшированный пароль пользователя. Обязательный.
        name (str): Имя пользователя. Необязательный.
        surname (str): Фамилия пользователя. Необязательный.
        patronymic (str): Отчество пользователя. Необязательный.
        birthday (datetime.date): Дата рождения пользователя. Необязательный.
        birth_time (datetime.time): Время рождения пользователя. Необяз.
        country (str): Страна проживания пользователя. Необязательный.
        city (str): Город проживания пользователя. Необязательный.
        phone (str): Номер телефона пользователя. Необязательный.
        avatar (str): Путь к файлу аватара пользователя. Необязательный.
        sex (str): Пол пользователя. Необязательный.
        premium (bool): Статус премиум-подписки пользователя. По умолчанию
        False (не премиум).
        zodiac_sign (str): Знак зодиака пользователя, вычисляется на основе
        даты рождения. Необязательный.
        natal_chart (relationship): Связь с моделью UserNatalChart для доступа
        к натальной карте пользователя. Использует внешний ключ и ленивую
        загрузку.

    Использование:
        Для создания нового пользователя используйте метод create класса
        BaseModel.
    """
    __tablename__ = 'user_SP'

    login = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    patronymic = db.Column(db.String(100), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    birth_time = db.Column(db.Time, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    sex = db.Column(db.String(10), nullable=True)
    premium = db.Column(db.Boolean, default=False)
    zodiac_sign = db.Column(db.String(15), nullable=True)
    natal_chart = db.relationship('UserNatalChart', backref='users', lazy=True)

    def __repr__(self) -> str:
        return (f'id: {self.id}\n'
                f'Логин: {self.login}\n'
                f'email: {self.email}\n')


class UserNatalChart(db.Model, BaseModel):
    """
    Модель натальной карты пользователя.

    Атрибуты:
        user_id (int): Идентификатор пользователя, к которому относится
                       натальная карта. Устанавливается как внешний ключ на
                       таблицу пользователей.
        natal_chart (str): Содержимое натальной карты в текстовом формате.
                           Хранит информацию о планетарных позициях, аспектах
                           и других астрологических данных пользователя.

    Использование:
        Для добавления натальной карты пользователя, сначала необходимо
        создать или получить экземпляр пользователя, затем создать экземпляр
        UserNatalChart с ссылкой на этого пользователя и сохранить в базе
        данных.
    """
    __tablename__ = "user_natal_chart_SP"

    user_id = db.Column(db.Integer, db.ForeignKey("user_SP.id"))
    natal_chart = db.Column(db.Text(), nullable=False)


class Horoscope(db.Model, BaseModel):
    """
    Модель гороскопа.

    Атрибуты:
        period (str): Период прогноза (например, "сегодня", "неделя", "месяц"). Может быть пустым, если
                      прогноз не привязан к конкретному периоду времени.
        zodiac_sign (str): Знак зодиака, для которого предназначен гороскоп. Может быть пустым, если
                           гороскоп общий и не привязан к конкретному знаку.
        horoscope (str): Текст гороскопа. Содержит прогнозы и советы для указанного знака зодиака
                         и периода. Должен быть заполнен.
        date (datetime.date): Дата, для которой актуален гороскоп. Помогает определить актуальность
                              прогноза.

    Использование:
        Для добавления нового гороскопа в базу данных, создайте экземпляр Horoscope с необходимыми
        атрибутами и используйте метод `create` для сохранения в базу данных.
    """
    __tablename__ = "horoscope_SP"

    period = db.Column(db.String(15), nullable=True)
    zodiac_sign = db.Column(db.String(15), nullable=True)
    horoscope = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date)


class UserTranzit(db.Model, BaseModel):
    __tablename__ = 'user_tranzit_SP'

    user_id = db.Column(db.Integer, db.ForeignKey('user_SP.id'))
    period = db.Column(db.String(15), nullable=True)
    tranzit = db.Column(db.Text(), nullable=False)


class DataAccess:
    """
    Класс для управления доступом к данными в приложении прогнозирования гороскопов.
    Методы:
        check_new_user(self, login: str, email: str, password: str) -> bool:
            Проверяет данные нового пользователя на уникальность и соответствие форматам.
            Возвращает True, если проверка пройдена успешно и регистрация возможна.

        add_user(self, forms):
            Создает нового пользователя с данными из формы регистрации.

        get_user(self, login: str, password: str) -> bool | None:
            Пытается аутентифицировать пользователя с заданными логином и паролем.
            Возвращает True, если аутентификация прошла успешно.

        add_profile(self, user, forms):
            Обновляет профиль пользователя данными из формы.

        add_avatar(self, current_user, file_path):
            Устанавливает новый аватар для пользователя.

        get_horoscope(self, period, date, zodiac_sign):
            Возвращает гороскоп для заданного знака зодиака, периода и даты.

        add_new_horoscope(self, period, zodiac_sign, text, date):
            Создает новый гороскоп с заданными параметрами.

        get_natal_chart(self, user_id):
            Возвращает натальную карту пользователя по его идентификатору.

        add_new_natal_cart(self, user_id, text):
            Создает новую натальную карту для пользователя.

        del_natal_chart(self, user_id):
        Удаляет натальную карту пользователя по его идентификатору.
    """
    def check_new_user(self, login: str, email: str, password: str) -> bool:
        """
        Проверяет нового пользователя на уникальность логина и электронной почты,
        а также соответствие логина, электронной почты и пароля заданным регулярным выражениям.

        Параметры:
            login (str): Логин нового пользователя. Должен быть уникальным и соответствовать
                         определенному формату (5-25 символов, включая буквы, цифры и специальные символы).
            email (str): Электронная почта нового пользователя. Должна быть уникальной и соответствовать
                         стандартному формату электронной почты.
            password (str): Пароль нового пользователя. Должен соответствовать определенному формату
                            (5-36 символов, включая буквы, цифры и специальные символы).

        Возвращает:
            bool: True, если пользователь успешно прошел проверку и может быть зарегистрирован.
                  Возвращает False и выводит соответствующие сообщения об ошибках через Flask flash,
                  если какое-либо условие не выполнено.

        Использование:
            result = check_new_user("newUserLogin", "user@example.com", "SecurePassword123!")
            if result:
                # Процедура регистрации нового пользователя
            else:
                # Обработка ошибок, пользователь не может быть зарегистрирован
        """
        # Регулярное выражение для логина: только латиница, цифры, "!", "?", длина 5-25 символов.
        pattern_login = r"^[a-zA-Z!?\d]{5,25}$"
        # Регулярное выражение для email: стандартный формат email с доменом верхнего уровня от 2 до 4 символов.
        pattern_email = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"
        # Регулярное выражение для пароля: латиница, цифры, "!", "?", длина 5-36 символов.
        pattern_password = r"^[a-zA-Z!?\d]{5,36}$"
        if User.query.filter_by(login=login).first():
            flash(
                {
                    "title": "Ошибка!",
                    "message": "Такой пользователь уже существует",
                },
                category="error",
            )
            return False
        elif User.query.filter_by(email=email).first():
            flash(
                {
                    "title": "Ошибка!",
                    "message": "Пользователь с таким E-mail уже есть",
                },
                category="error",
            )
            return False
        elif re.match(pattern_login, login) is None:
            flash(
                {
                    "title": "Ошибка!",
                    "message": "Логин должен состоять из 5-25 латинских букв, "
                    "цифр и символов!",
                },
                category="error",
            )
            return False
        elif re.match(pattern_email, email) is None:
            flash(
                {
                    "title": "Ошибка!",
                    "message": "Вы ввели неверный формат почты!",
                },
                category="error",
            )
            return False
        elif re.match(pattern_password, password) is None:
            flash(
                {
                    "title": "Ошибка!",
                    "message": "Пароль должен состоять из 5-36 латинских букв, "
                    "цифр и символов",
                },
                category="error",
            )
            return False
        flash(
            {
                "title": "Успешно!",
                "message": "Вы успешно зарегистрированы, зайдите в кабинет",
            },
            category="success",
        )
        return True

    def add_user(self, forms: dict) -> None:
        """
        Создает нового пользователя, хешируя пароль для безопасности перед сохранением.

        Параметры:
            forms (dict): Словарь с данными формы регистрации пользователя.
        """
        forms["password"] = generate_password_hash(forms["password"])
        User.create(**forms)

    def get_user(self, login: str, password: str, remeber) -> bool | None:
        """
        Аутентифицирует пользователя на основе предоставленного логина и пароля.

        Параметры:
            login (str): Логин пользователя для аутентификации.
            password (str): Пароль пользователя для проверки.

        Возвращает:
            True: Если аутентификация прошла успешно (пользователь найден и пароль верный).
            None: Если пользователь не найден или пароль не верный.
        """
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remeber)
            return True

    def add_profile(self, user: User, forms: dict) -> None:
        """
        Обновляет профиль пользователя с данными из формы.

        Параметры:
        user (User): Объект пользователя, чей профиль необходимо обновить.
        forms (dict): Словарь с данными формы. Ключи соответствуют полям объекта пользователя.

        Действия:
            - Преобразует строку даты рождения в объект даты и обновляет поле `birthday`.
            - Преобразует строку времени рождения в объект времени и обновляет поле `birth_time`.
            - Вычисляет знак зодиака на основе новой даты рождения и обновляет поле `zodiac_sign`.
            - Обновляет остальные поля пользователя данными из формы, если они предоставлены.

        Возвращает:
            None. Метод обновляет данные в базе данных и не возвращает значение.
        """
        birthday = forms.get("birthday")
        birth_time = forms.get("birth_time")
        if birthday:
            user.birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
            user.zodiac_sign = get_zodiac_sign(user.birthday)

        if birth_time:
            user.birth_time = datetime.strptime(birth_time, "%H:%M").time()
        for key, value in forms.items():
            if value:
                setattr(user, key, value)
        db.session.commit()

    def add_avatar(self, current_user: User, file_path: str) -> None:
        """
        Устанавливает или обновляет путь к файлу аватара для текущего пользователя.

        Параметры:
        current_user (User): Объект пользователя, чей аватар необходимо обновить.
        file_path (str): Строка, содержащая путь к новому файлу аватара пользователя.

        Возвращает:
            None. Метод выполняет обновление данных в базе данных и не возвращает значение.
        """
        current_user.avatar = file_path
        db.session.commit()

    def get_horoscope(self, period: str, date: datetime.date, zodiac_sign: str) -> Horoscope:
        """
        Возвращает гороскоп для указанного периода, даты и знака зодиака.

        Параметры:
            period (str): Период времени гороскопа (например, "день", "неделя").
            date (datetime.date): Дата, на которую запрашивается гороскоп.
            zodiac_sign (str): Знак зодиака, для которого запрашивается гороскоп.

        Возвращает:
            Horoscope: Экземпляр модели `Horoscope`, соответствующий заданным критериям.
                       Возвращает None, если подходящий гороскоп не найден.
        """
        horoscope = Horoscope.query.filter_by(
            period=period, date=date, zodiac_sign=zodiac_sign
        ).first()
        return horoscope

    def add_new_horoscope(self, period: str, zodiac_sign: str, text: str, date: datetime.date) -> None:
        """
        Добавляет новый гороскоп в базу данных.

        Параметры:
            period (str): Период гороскопа (например, "день", "неделя", "месяц").
            zodiac_sign (str): Знак зодиака, для которого предназначен гороскоп.
            text (str): Текст гороскопа, содержащий прогноз.
            date (datetime.date): Дата, на которую предоставлен прогноз.

        Возвращает:
            None. Метод не возвращает значение, но результатом его выполнения является
            добавление новой записи в таблицу гороскопов.
        """
        new_horoscope = Horoscope(
            period=period,
            zodiac_sign=zodiac_sign,
            horoscope=text,
            date=date,
        )
        db.session.add(new_horoscope)
        db.session.commit()

    def get_natal_chart(self, user_id: int) -> UserNatalChart:
        """
        Извлекает натальную карту пользователя по его идентификатору.

        Параметры:
            user_id (int): Идентификатор пользователя, натальную карту которого необходимо получить.

        Возвращает:
            UserNatalChart: Экземпляр модели `UserNatalChart`, соответствующий заданному пользователю.
                            Возвращает `None`, если натальная карта для пользователя не найдена.

        """
        natal_chart = UserNatalChart.query.filter_by(user_id=user_id).first()
        return natal_chart

    def add_new_natal_cart(self, user_id: int, text: str) -> None:
        """
        Создаёт новую натальную карту для указанного пользователя и сохраняет её в базе данных.

        Параметры:
            user_id (int): Идентификатор пользователя, для которого создаётся натальная карта.
            text (str): Текст натальной карты, содержащий астрологические данные и интерпретации.

        Возвращает:
            None. Метод не возвращает значение, но вносит изменения в базу данных, добавляя новую запись.

        """
        new_natal_cart = UserNatalChart(user_id=user_id, natal_chart=text)
        db.session.add(new_natal_cart)
        db.session.commit()

    def del_natal_chart(self, user_id: int) -> None:
        """
        Создаёт новую натальную карту для указанного пользователя и сохраняет
        её в базе данных.

        Параметры:
            user_id (int): Идентификатор пользователя.

        Возвращает:
            None. Метод не возвращает значение, но вносит изменения
            в базу данных, удаляя неактуальную натальную карту.
        """
        natal_chart = UserNatalChart.query.filter_by(user_id=user_id).first()
        if natal_chart:
            db.session.delete(natal_chart)
            db.session.commit()

@manager.user_loader
def load_user(user_id: int) -> User:
    """
    Callback функция для Flask-Login, которая используется для загрузки объекта пользователя.

    Параметры:
        user_id (str): Строковый идентификатор пользователя, используемый для поиска в базе данных.

    Возвращает:
        User: Объект пользователя, соответствующий идентификатору. Возвращает None, если
              пользователь не найден.
    """
    return User.query.get(user_id)


with app.app_context():
    db.create_all()
