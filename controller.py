import os
from datetime import datetime

from flask import render_template, Response, redirect, url_for, request, flash
from flask_login import login_required, logout_user, login_user, current_user
from zodiac_sign import get_zodiac_sign

from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, manager, db
from business_logic import check_new_user, allowed_file


from test_logic import GetHoroscope


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
    forms = dict(request.form)
    if forms['password'] != forms['confirm_password']:
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Пароль не совпадает',
            },
            category='error',
        )
        return render_template('register_authorization.html')
    forms.pop('confirm_password', None)
    if check_new_user(**forms):
        forms['password'] = generate_password_hash(forms['password'])
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


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile() -> Response | str:
    """
    Views для отображения и изменения профиля
    """
    if request.method == 'GET':
        return render_template('profile.html')
    user = current_user
    forms = dict(request.form)
    if forms['birthday']:
        forms['birthday'] = datetime.strptime(forms['birthday'], '%Y-%m-%d').date()
        forms['zodiac_sign'] = get_zodiac_sign(forms['birthday'], language='ru-RU')
    if forms['birth_time']:
        forms['birth_time'] = datetime.strptime(forms['birth_time'], '%H:%M').time()
    for key, value in forms.items():
        if value:
            setattr(user, key, value)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('profile.html')
    file = request.files['photo']
    if file.filename == '':
        return redirect('profile')
    if not (file and allowed_file(file.filename)):
        flash({'title': 'Ошибка!', 'message': 'Неверный файл'})
        return redirect('profile')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = secure_filename(f'{timestamp}_{file.filename}')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    current_user.avatar = file_path
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/horoscope/<period>')
def horoscope(period) -> Response | str:
    """
        Views для отображения гороскопа на день
    """
    user_horoscope = current_user.zodiac_sign
    get_horoscope = GetHoroscope(user_horoscope, period)
    text = get_horoscope.get_response()
    return render_template('chat.html', text=text)


@app.route('/natal_chart')
def natal_chart() -> Response | str:
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
    return User.query.filter_by(id=user_id).first()
