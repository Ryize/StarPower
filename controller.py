import os

from datetime import datetime

from flask import render_template, Response, redirect, url_for, request, flash, jsonify
from flask_login import login_required, logout_user, current_user

from werkzeug.utils import secure_filename

from models import DataAccess, UserNatalChart
from app import app, db
from business_logic import allowed_file, date_horoscope, delete_file

from horoscope_logic import GetHoroscope, GetNatalChart, GetSpecialHoroscope

from admin_panel import admin
from natal_chart_logic import GetNatalChart2


# экземпляр класса для работы с БД
dataAccess = DataAccess()


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
    # Проверка данных в форме ригистрации
    if dataAccess.check_new_user(**forms):
        # Добавление нового пользователя в БД
        dataAccess.add_user(forms)
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
    # Получение пользователя из БД
    if dataAccess.get_user(login, password):
        # Перенаправление в админ-панель, если пользователь - админ
        if login == 'Admin':
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
    if user.birth_time != forms['birth_time'] or user.birthday != forms['birthday']:
        natal_chart = UserNatalChart.query.filter_by(user_id=user.id).first()
        db.session.delete(natal_chart)
        db.session.commit()
    # Добавление данных в профиль текущего пользователя
    dataAccess.add_profile(user, forms)
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
    if current_user.avatar:
        delete_file(current_user.avatar)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = secure_filename(f'{timestamp}_{file.filename}')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    # Добавить путь к аватру пользователя в БД
    dataAccess.add_avatar(current_user, file_path)
    flash(
        {'title': 'Успех!',
         'message': 'Ваша картинка обновлена'
         },
        category='success',
    )
    return redirect(url_for('profile'))


@app.route('/horoscope/<period>')
@login_required
def horoscope(period) -> Response | str:
    """
        Views для отображения гороскопа на день
    """
    # сделать проверку данных и перекинуть для заполнения на profile
    if not (current_user.birthday or current_user.birth_time):
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
    # Поиск подходящего гороскопа по заданным параметрам в БД
    horoscope = dataAccess.get_horoscope(period, date, zodiac_sign)
    if not horoscope:
        get_horoscope = GetHoroscope(zodiac_sign, period)
        text = get_horoscope.get_response()
        # Добавление нового гороскопа в БД
        dataAccess.add_new_horoscope(period, zodiac_sign, text, date)
        return render_template('horoscope_chat.html', text=text)
    return render_template('horoscope_chat.html', text=horoscope.horoscope)


@app.route('/specialhoroscope/', methods=['POST'])
@login_required
def specialhoroscope() -> Response | str:
    """
        Views для отображения специального гороскопа
    """
    # сделать проверку данных и перекинуть для заполнения на profile
    if not (current_user.birthday or current_user.birth_time):
        flash(
            {
                'title': 'Заполните данные',
                'message': 'Для создания гороскопа заполните данные',
            },
            category='error',
        )
        return redirect(url_for('profile'))

    form = request.form

    sp_date = form.get('sp_date')
    sp_date = datetime.strptime(sp_date, "%Y-%m-%d")
    period = 'special'
    zodiac_sign = current_user.zodiac_sign
    # Поиск подходящего гороскопа по заданным параметрам в БД
    horoscope = dataAccess.get_horoscope(period, sp_date, zodiac_sign)
    if not horoscope:
        get_horoscope = GetSpecialHoroscope(sp_date, zodiac_sign)
        text = get_horoscope.get_response()
        # Добавление нового гороскопа в БД
        dataAccess.add_new_horoscope(period, zodiac_sign, text, sp_date)
        return render_template('horoscope_chat.html', text=text)
    return render_template('horoscope_chat.html', text=horoscope.horoscope)


@app.route('/natal_chart', methods=['GET', 'POST'])
@login_required
def natal_chart() -> Response | str:
    """
        Views для отображения гороскопа на определенный день
    """
    # сделать проверку данных и перекинуть для заполнения на profile
    if request.method == 'GET':
        if not (current_user.birthday or current_user.birth_time):
            flash(
                {
                    'title': 'Заполните данные',
                    'message': 'Для создания гороскопа заполните данные',
                },
                category='error',
            )
            return redirect(url_for('profile'))
        return render_template('chat.html')
    # Получение натальной карты из БД текущего пользователя
    natal_cart = dataAccess.get_natal_chart(current_user.id)
    if natal_cart:
        return jsonify({
            'success': True,
            'natal_chart': natal_cart.natal_chart,
        })
    date = datetime.combine(current_user.birthday, current_user.birth_time)
    text = GetNatalChart2(date, current_user.city).natal_chart()
    # Добавление новой натальной карты в БД
    dataAccess.add_new_natal_cart(current_user.id, text)
    return jsonify({
        'success': True,
        'natal_chart': text,
    })


@app.route('/logout/')
@login_required
def logout() -> Response | str:
    """
    Views для выхода из профиля пользователя
    """
    logout_user()
    return redirect(url_for('index'))


@app.after_request
def redirect_to_sign(response):
    if response.status_code == 401:
        return redirect(url_for('register_authorization'))
    return response
