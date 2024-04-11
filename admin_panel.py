from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required

from app import app, db
from models import Horoscope, User, UserNatalChart


class MyAdminIndexView(AdminIndexView):
    """
    Переопределение AdminIndexView для контроля доступа к главной странице
    админ-панели.
    """

    @login_required
    def is_accessible(self):
        """
        Проверка доступа текущего пользователя к главной странице админ-панели.
        """
        return current_user.is_authenticated and current_user.login == 'Admin'

    def inaccessible_callback(self, name, **kwargs):
        """
        Перенаправление на страницу входа, если пользователь не авторизован
        или не является администратором.
        """
        return redirect(url_for('authorization'))


class MyModelView(ModelView):
    """
    Переопределение ModelView для контроля доступа к админ-панели.
    """

    @login_required
    def is_accessible(self):
        """
        Проверка доступа текущего пользователя к админ-панели.
        """
        if current_user.is_authenticated and current_user.login == 'Admin':
            return redirect(url_for('admin_panel'))

    def inaccessible_callback(self, name, **kwargs):
        """
        Перенаправление на страницу входа, если пользователь не авторизован
        или не является администратором.
        """
        return redirect(url_for('index'))


admin = Admin(app, name='Административная панель', template_mode='bootstrap3',
              index_view=MyAdminIndexView())

admin.add_view(MyModelView(User, db.session, name='Пользователи'))
admin.add_view(MyModelView(UserNatalChart, db.session,
                           name='Натальные карты пользователей'))
admin.add_view(MyModelView(Horoscope, db.session, name='Гороскопы'))


@app.route('/admin')
@login_required
def admin_panel():
    return redirect('admin.index')
