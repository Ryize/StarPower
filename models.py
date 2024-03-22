from datetime import datetime, timezone
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from flask_login import login_user

from flask_login import UserMixin
from zodiac_sign import get_zodiac_sign

from app import db, app, manager


class BaseModel:
    """
    :param id: уникальный идентификатор рецепта
    :type id: int
    :param created_at: дата и время создания записи о пользователе
    :type created_at: datetime
    """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc))

    def save(self) -> None:
        """
        Сохраняет текущий экземпляр класса в базе данных

        :return: None
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def create(cls, *args, **kwargs) -> 'BaseModel':

        new_obj = cls(*args, **kwargs)
        new_obj.save()
        return new_obj


class User(db.Model, BaseModel, UserMixin):
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
        return (
            f'id: {self.id}\n'
            f'Логин: {self.login}\n'
            f'email: {self.email}\n'
            )


class UserNatalChart(db.Model, BaseModel):
    __tablename__ = 'user_natal_chart_SP'

    user_id = db.Column(db.Integer, db.ForeignKey('user_SP.id'))
    natal_chart = db.Column(db.Text(), nullable=False)


class Horoscope(db.Model, BaseModel):
    __tablename__ = 'horoscope_SP'

    period = db.Column(db.String(15), nullable=True)
    zodiac_sign = db.Column(db.String(15), nullable=True)
    horoscope = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date)


class DataAccess:

    def check_new_user(self, login: str, email: str, password: str) -> bool:
        """
        Проверяет данные нового пользователя перед регистрацией.

        pattern_login - Эта регулярка проверяет,
        соответствует ли строка следующим условиям:
        Длина строки от 5 до 25 символов.
        Строка может содержать только латинские буквы в верхнем и нижнем регистре,
        цифры, а также символы !, ?,.
        Строка не должна содержать пробелы или другие специальные символы.

        pattern_email - Она проверяет наличие символа '@' в строке
        и наличие хотя бы одного символа до и после символа '@'.
        Допустимыми символами являются буквы, цифры, дефисы и точки.
        За символом '@' должна следовать доменная часть email-адреса,
        состоящая из букв, цифр, дефисов и точек, где точка не может быть первым
        или последним символом, и между точками должен быть хотя бы один символ.
        В конце доменной части должен быть указан домен верхнего уровня
        из двух-четырех символов, например '.com' или '.ru'.

        pattern_password - Проверяет, что строка содержит от 5 до 36 символов,
        состоящих из букв (в любом регистре), цифр и знаков !, ? или _.
        То есть, данное регулярное выражение подходит для проверки корректности
        пароля, который должен содержать только разрешенные символы и быть длиной
        не менее 5 и не более 36 символов.

        :param login: логин пользователя.
        :type login: str
        :param email: электронная почта пользователя.
        :type email: str
        :param password: пароль пользователя.
        :type password: str
        :return: результат проверки.
        :rtype: bool
        """
        pattern_login = r'^[a-zA-Z!?\d]{5,25}$'
        pattern_email = r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$'
        pattern_password = r'^[a-zA-Z!?\d]{5,36}$'
        if User.query.filter_by(login=login).first():
            flash(
                {
                    'title': 'Ошибка!',
                    'message': 'Такой пользователь уже существует',
                },
                category='error',
            )
            return False
        elif User.query.filter_by(email=email).first():
            flash(
                {
                    'title': 'Ошибка!',
                    'message': 'Пользователь с таким E-mail уже есть',
                },
                category='error',
            )
            return False
        elif re.match(pattern_login, login) is None:
            flash(
                {
                    'title': 'Ошибка!',
                    'message': 'Логин должен состоять из 5-25 латинских букв, '
                            'цифр и символов!',
                },
                category='error',
            )
            return False
        elif re.match(pattern_email, email) is None:
            flash(
                {
                    'title': 'Ошибка!',
                    'message': 'Вы ввели неверный формат почты!',
                },
                category='error',
            )
            return False
        elif re.match(pattern_password, password) is None:
            flash(
                {
                    'title': 'Ошибка!',
                    'message': 'Пароль должен состоять из 5-36 латинских букв, '
                            'цифр и символов',
                },
                category='error',
            )
            return False
        flash(
            {
                'title': 'Успешно!',
                'message': 'Вы успешно зарегистрированы, зайдите в кабинет',
            },
            category='success',
        )
        return True

    def add_user(self, forms):
        forms['password'] = generate_password_hash(forms['password'])
        User.create(**forms)

    def get_user(self, login: str, password: str) -> bool | None:
        """
        Получение пользователя из базы данных и проверка введенного пароля.

        Args:
            name (str): имя пользователя.
            surname (str): фамилия пользователя.
            password (str): пароль пользователя.

        Returns:
            bool: True, если пользователь найден и пароль верен,
                  None в противном случае.
        """
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return True

    def add_profile(self, user, forms):
        birthday = forms.get('birthday')
        birth_time = forms.get('birth_time')
        if birthday:
            user.birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
            user.zodiac_sign = get_zodiac_sign(user.birthday)

        if birth_time:
            user.birth_time = datetime.strptime(birth_time, '%H:%M').time()
        for key, value in forms.items():
            if value:
                setattr(user, key, value)
        db.session.commit()

    def add_avatar(self, current_user, file_path):
        current_user.avatar = file_path
        db.session.commit()

    def get_horoscope(self, period, date, zodiac_sign):
        horoscope = Horoscope.query.filter_by(period=period,
                                              date=date,
                                              zodiac_sign=zodiac_sign
                                              ).first()
        return horoscope

    def add_new_horoscope(self, period, zodiac_sign, text, date):
        new_horoscope = Horoscope(
            period=period,
            zodiac_sign=zodiac_sign,
            horoscope=text,
            date=date,
        )
        db.session.add(new_horoscope)
        db.session.commit()

    def get_natal_chart(self, user_id):
        natal_chart = UserNatalChart.query.filter_by(user_id=user_id).first()
        return natal_chart

    def add_new_natal_cart(self, user_id, text):
        new_natal_cart = UserNatalChart(user_id=user_id,
                                        natal_chart=text
                                        )
        db.session.add(new_natal_cart)
        db.session.commit()


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


with app.app_context():
    db.create_all()
