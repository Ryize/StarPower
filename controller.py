from flask import render_template, Response, redirect, url_for, request, flash
from flask_login import login_required, logout_user, login_user
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, manager
from business_logic import check_new_user


@app.route('/')
@app.route('/index/')
def index() -> Response | str:
    """
        Views для главной страницы.
    """
    return render_template('index.html')

@app.route('/register_authorization', methods=['GET', 'POST'])
def register_authorization() -> Response | str:
    """
        Views для страницы регистрации и авторизации
    """
    return render_template('register_authorization.html')


@app.route('/register', methods=['GET', 'POST'])
def register() -> Response | str:
    """
        Views для страницы регистрации пользователя.
    """
    if request.method == 'GET':
        return render_template('register_authorization.html')
    login = request.form.get('login')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    if password != confirm_password:
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Пароль не совпадает',
            },
            category='error',
        )
        return render_template('register_authorization.html')
    if check_new_user(login=login, email=email, password=password):
        forms = dict(request.form)
        forms = forms.pop('confirm_password', None)
        forms['password'] = generate_password_hash(password)
        User.create(**forms)
        return redirect(url_for('register_authorization'))
    return render_template('register_authorization.html')


@app.route('/authorization', methods=['GET', 'POST'])
def authorization() -> Response | str:
    """
        Views для страницы авторизации пользователя.
    """
    if request.method == 'GET':
        return render_template('register_authorization.html')
    login = request.form.get('login')
    password = request.form.get('password')
    user = User.query.filter_by(login=login).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        flash(
            {'title': 'Успешно!', 'message': 'Добро пожаловать'},
            category='success',
        )
        return redirect(url_for('index'))
    flash(
        {
            'title': 'Ошибка!',
            'message': 'Мы не нашли такого пользователя',
        },
        category='error',
    )
    return render_template('register_authorization.html')


@app.route('/profile')
def profile() -> Response | str:
    """
    Views для отображения и изменения профиля
    """
    return render_template('profile.html')


@app.route('/daily_horoscope')
def daily_horoscope() -> Response | str:
    """
        Views для отображения гороскопа на день
    """
    return render_template('chat.html')


@app.route('/weekly_horoscope')
def weekly_horoscope() -> Response | str:
    """
        Views для отображения гороскопа на неделю
    """
    return render_template('chat.html')


@app.route('/monthly_horoscope')
def monthly_horoscope() -> Response | str:
    """
        Views для отображения гороскопа на месяц
    """
    return render_template('chat.html')


@app.route('/special_horoscope')
def special_horoscope() -> Response | str:
    """
        Views для отображения гороскопа на определенный день
    """
    return render_template('chat.html')


@app.route('/logout/')
@login_required
def logout() -> Response | str:
    """
    Views для выхода из профиля пользователя
    """
    logout_user()
    return redirect(url_for('index'))


@manager.user_loader
def load_user(user_id):
    return User.get(user_id)