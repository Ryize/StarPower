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
        new_user = cls(*args, **kwargs)
        new_user.save()

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

    login = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


@manager.user_loader
def load_user(user_id: int) -> User | None:
    """
    Загружает пользователя из базы данных по заданному идентификатору.

    :param user_id: идентификатор пользователя
    :type user_id: int
    :return: объект пользователя, если пользователь существует, иначе None
    :rtype: User
    """
    return User.query.get(user_id)


with app.app_context():
    db.create_all()