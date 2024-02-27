import datetime

from flask_login import UserMixin

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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def save(self) -> None:
        """
        Сохраняет текущий экземпляр класса в базе данных

        :return: None
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def create(cls, *args, **kwargs) -> 'BaseModel':
        """
        Позволяет создать новый объект в базе данных.

        :param args: Позиционные аргументы для передачи конструктору модели
        :type args: tuple
        :param kwargs: Аргументы ключевого слова для передачи конструктору модели.
        :type kwargs: dict
        :return: None
        """
        new_obj = cls(*args, **kwargs)
        new_obj.save()
        return new_obj


class User(db.Model, BaseModel, UserMixin):
    """
    Модель пользователя.

    :param id: уникальный идентификатор пользователя
    :type id: int
    :param login: логин пользователя
    :type login: str
    :param email: адрес электронной почты пользователя
    :type email: str
    :param password: пароль пользователя
    :type password: str
    """
    __tablename__ = 'user'

    login = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
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
    zodiac_sign_id = db.Column(db.Integer, db.ForeignKey('zodiac_sign.id'), nullable=True)


class ZodiacSign(db.Model, BaseModel):

    __tablename__ = 'zodiac_sign'

    name = db.Column(db.String(50), unique=True, nullable=False)


class UserHoroscope(db.Model, BaseModel):
    __tablename__ = 'user_horoscope'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    natal_chart = db.Column(db.String(700))

# class HoroscopeToday(db.Model, BaseModel):
#     date = db.Column(db.String())
#     zodiac_sign = db.Column(db.String(100))
#     horoscope = db.Column(db.String(100))
#
#
# class HoroscopeWeek(db.Model, BaseModel):
#     date = db.Column(db.String())
#     zodiac_sign = db.Column(db.String(100))
#     horoscope = db.Column(db.String(100))
#
#
# class HoroscopeMonth(db.Model, BaseModel):
#     date = db.Column(db.String())
#     zodiac_sign = db.Column(db.String(100))
#     horoscope = db.Column(db.String(100))
#
#
# class HoroscopeYear(db.Model, BaseModel):
#     date = db.Column(db.String())
#     zodiac_sign = db.Column(db.String(100))
#     horoscope = db.Column(db.String(100))


@manager.user_loader
def load_user(user_id: int) -> User | None:
    """
    Загружает пользователя из базы данных по заданному идентификатору.

    :param user_id: идентификатор пользователя
    :type user_id: int
    :return: объект пользователя, если пользователь существует, иначе None
    :rtype: User
    """
    return User.query.filter_by(id=user_id).first()


with app.app_context():
    db.create_all()