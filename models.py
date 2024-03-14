from datetime import datetime, timezone

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
    sex = db.Column(db.Boolean, default=False, nullable=True)
    premium = db.Column(db.Boolean, default=False)
    zodiac_sign = db.Column(db.String(15), nullable=True)
    natal_chart = db.relationship('UserNatalChart', backref='users', lazy=True)


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
