import os

from datetime import datetime

from flask import render_template, Response, redirect, url_for, request, flash
from flask_login import login_required, logout_user, login_user, current_user

from werkzeug.utils import secure_filename

from zodiac_sign import get_zodiac_sign

from models import User, Horoscope, UserNatalChart
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, manager, db
from business_logic import check_new_user, allowed_file, date_horoscope

from test_logic import GetHoroscope, GetNatalChart

from admin_panel import admin  # Добавленный импорт для админ-панели



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
        # Перенаправление в админ-панель, если пользователь - админ
        if user.login == 'Admin':
            return redirect(url_for('admin.index'))
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
        if current_user.birth_time:
            birth_time = current_user.birth_time.strftime('%H:%M')
            return render_template('profile.html', birth_time=birth_time)
        return render_template('profile.html')
    user = current_user
    forms = request.form

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
    flash(
        {'title': 'Успех!',
         'message': 'Ваши данные успешно сохранены'
         },
        category='success',
    )
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
    db.session.commit()
    flash(
        {'title': 'Успех!',
         'message': 'Ваша картинка обновлена'
         },
        category='success',
    )
    return redirect(url_for('profile'))


@app.route('/horoscope/<period>')
def horoscope(period) -> Response | str:
    """
        Views для отображения гороскопа на день
    """
    # сделать проверку данных и перекинуть для заполнения на profile
    if not current_user.birthday or not current_user.birth_time:
        flash(
            {
                'title': 'Заполните данные',
                'message': 'Для создания гороскопа заполните данные',
            },
            category='error',
        )
        return redirect(url_for('profile'))

    date = date_horoscope(period)

    zodiac_sign = current_user.zodiac_sign
    horoscope = Horoscope.query.filter_by(period=period, date=date, zodiac_sign=zodiac_sign).first()
    if not horoscope:
        user_horoscope = current_user.zodiac_sign
        get_horoscope = GetHoroscope(user_horoscope, period)
        text = get_horoscope.get_response()
        new_horoscope = Horoscope(
            period=period,
            zodiac_sign=zodiac_sign,
            horoscope=text,
            date=date,
        )
        db.session.add(new_horoscope)
        db.session.commit()
        return render_template('chat.html', text=text)
    return render_template('chat.html', text=horoscope.horoscope)

@app.route('/natal_chart')
def natal_chart() -> Response | str:
    """
        Views для отображения гороскопа на определенный день
    """
    # сделать проверку данных и перекинуть для заполнения на profile
    natal_cart = UserNatalChart.query.filter_by(user_id=current_user.id).first()
    if natal_cart:
        return render_template('chat.html', text=natal_cart.natal_chart)
    date = datetime.combine(current_user.birthday, current_user.birth_time)
    text = GetNatalChart(date, current_user.city).get_response()
    new_natal_cart = UserNatalChart(
        user_id=current_user.id,
        natal_chart=text
        )
    db.session.add(new_natal_cart)
    db.session.commit()
    return render_template('chat.html', text=text)



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
