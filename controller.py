from flask import render_template, Response, redirect, url_for, request, flash
from flask_login import login_required, logout_user, login_user
from sqlalchemy.testing.pickleable import User
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
    return render_template('register_authorization.html')


@app.route('/register', methods=['GET', 'POST'])
def register() -> Response | str:
    """
        Views для страницы регистрации пользователя.
    """
    if request.method == 'GET':
        return render_template('register_authorization.html')
    login = request.form.get('login', '_')
    email = request.form.get('email')
    password = request.form.get('password', '_')
    password2 = request.form.get('password2', '_')
    if password != password2:
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Парольне совпадает',
            },
            category='error',
        )
        return render_template('register_authorization.html')
    if check_new_user(login=login, email=email, password=password):
        forms = dict(request.form)
        forms['password'] = generate_password_hash(password)
        User.create(**forms)
        return redirect(url_for('authorization'))
    return render_template('register_authorization.html')



@app.route('/authorization', methods=['GET', 'POST'])
def authorization() -> Response | str:
    """
        Views для страницы авторизации пользователя.
    """
    if request.method == 'GET':
        return render_template('register_authorization.html')
    email = request.form.get('email', '_')
    password = request.form.get('password', '_')
    user = User.query.filter_by(email=email).first()
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