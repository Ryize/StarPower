"""
Модуль Controller для Flask-приложения прогнозирования гороскопов.

Этот модуль содержит представления, которые обрабатывают запросы от пользователя и возвращают соответствующие ответы.
Он взаимодействует с моделями для получения данных и передает эти данные в шаблоны для отображения пользователям.
Каждое представление ассоциировано с одним или несколькими URL-адресами.

Функции:
- index(): Отображает главную страницу приложения.
- register_authorization(): Обрабатывает страницу с формами регистрации и авторизации.
- register(): Регистрирует нового пользователя в системе.
- authorization(): Авторизует пользователя в системе.
- profile(): Позволяет пользователю просматривать и редактировать свой профиль.
- upload(): Обрабатывает загрузку и сохранение аватара пользователя.
- horoscope(): Выводит гороскоп пользователя на определенный период.
- specialhoroscope(): Выводит специализированный гороскоп на основе дополнительных данных.
- natal_chart(): Генерирует и отображает натальную карту пользователя.
- logout(): Выполняет выход пользователя из системы.
- redirect_to_sign(): Перенаправляет неавторизованных пользователей на страницу входа.

Все представления, за исключением logout() и redirect_to_sign(), используют декоратор @login_required для ограничения доступа только для авторизованных пользователей.
"""

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


@app.route("/")
@app.route("/index/")
def index() -> Response | str:
    """
    Views для главной страницы.
    """
    return render_template("index.html")


@app.route("/register_authorization", methods=["GET", "POST"])
def register_authorization() -> Response | str:
    """
    Views для страницы регистрации и авторизации
    """
    return render_template("register_authorization.html")


@app.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    """
    Views для страницы регистрации пользователя.

    GET запрос:
    Возвращает страницу с формой для регистрации и авторизации.

    POST запрос:
    Извлекает из запроса данные формы, включая 'login', 'password' и 'confirm_password'.
    Проверяет, что пароли совпадают и что пользователь с таким 'login' еще не зарегистрирован
    в базе данных. Если проверка прошла успешно, то создает нового пользователя,
    удаляя из данных формы 'confirm_password', и перенаправляет на страницу авторизации.
    В случае, если пароли не совпадают или пользователь с таким 'login' уже существует,
    пользователю выводится соответствующее сообщение об ошибке.

    :return: render_template('register_authorization.html') в случае GET запроса или ошибки регистрации,
             redirect(url_for('register_authorization')) в случае успешной регистрации.
    """
    if request.method == "GET":
        return render_template("register_authorization.html")
    forms = dict(request.form)
    if forms["password"] != forms["confirm_password"]:
        flash(
            {
                "title": "Ошибка!",
                "message": "Пароль не совпадает",
            },
            category="error",
        )
        return render_template("register_authorization.html")
    forms.pop("confirm_password", None)
    if dataAccess.check_new_user(**forms):
        dataAccess.add_user(forms)
        return redirect(url_for("register_authorization"))
    return render_template("register_authorization.html")


@app.route("/authorization", methods=["GET", "POST"])
def authorization() -> Response | str:
    """
    Views для страницы авторизации пользователя.

    GET запрос:
    Возвращает страницу с формой для регистрации и авторизации.

    POST запрос:
    Извлекает из запроса 'login' и 'password'. Проверяет наличие пользователя с такими данными
    в базе данных. Если пользователь найден, происходит его авторизация. Для пользователя с ролью 'Admin'
    осуществляется перенаправление на административную панель. В случае успешной авторизации
    выводится приветственное сообщение и перенаправление на главную страницу. Если пользователь
    не найден, выводится сообщение об ошибке.

    :return: render_template('register_authorization.html') в случае GET запроса или неудачной авторизации,
             redirect(url_for('index')) при успешной авторизации,
             redirect(url_for('admin.index')) если пользователь - админ.
    """
    if request.method == "GET":
        return render_template("register_authorization.html")
    login = request.form.get("login")
    password = request.form.get("password")
    # Получение пользователя из БД
    if dataAccess.get_user(login, password):
        # Перенаправление в админ-панель, если пользователь - админ
        if login == "Admin":
            return redirect(url_for("admin.index"))
        flash(
            {"title": "Успешно!", "message": "Добро пожаловать"},
            category="success",
        )
        return redirect(url_for("index"))
    flash(
        {
            "title": "Ошибка!",
            "message": "Мы не нашли такого пользователя",
        },
        category="error",
    )
    return render_template("register_authorization.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile() -> Response | str:
    """
    Views для отображения и изменения профиля пользователя.

    GET запрос:
    Отображает страницу профиля пользователя. Если у пользователя указано время рождения,
    оно также отображается на странице в соответствующем формате.

    POST запрос:
    Принимает измененные данные профиля пользователя из формы. Если данные о времени рождения
    или дате рождения изменены, существующая натальная карта пользователя удаляется из базы данных,
    предполагая необходимость создания новой. После обновления данных профиля в базе данных,
    пользователю выводится сообщение об успешном сохранении изменений и происходит перенаправление
    на страницу профиля.

    :return: render_template('profile.html') в случае GET запроса, с данными о времени рождения,
             если оно указано,
             redirect(url_for('profile')) после обновления данных профиля в случае POST запроса.
    """
    if request.method == "GET":
        if current_user.birth_time:
            birth_time = current_user.birth_time.strftime("%H:%M")
            return render_template("profile.html", birth_time=birth_time)
        return render_template("profile.html")
    user = current_user
    forms = request.form
    if user.birth_time != forms["birth_time"] or user.birthday != forms["birthday"]:
        natal_chart = UserNatalChart.query.filter_by(user_id=user.id).first()
        db.session.delete(natal_chart)
        db.session.commit()
    # Добавление данных в профиль текущего пользователя
    dataAccess.add_profile(user, forms)
    flash(
        {"title": "Успех!", "message": "Ваши данные успешно сохранены"},
        category="success",
    )
    return redirect(url_for("profile"))


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    """
    Обрабатывает загрузку аватара пользователя.

    POST запрос:
    Принимает файл изображения (фото) от пользователя. Проверяет, что файл не пустой
    и соответствует разрешенным типам файлов. Если файл валиден, предыдущий аватар пользователя
    удаляется (если он существует), и загруженный файл сохраняется в заданной директории
    с уникальным именем файла, основанным на текущем времени. Путь к новому файлу аватара
    добавляется в профиль пользователя в базе данных. Пользователь получает уведомление об успешной
    загрузке файла.

    В случае ошибки (если файл не выбран, не соответствует разрешенным типам или другая ошибка
    загрузки), пользователю отображается соответствующее сообщение об ошибке.

    :return: redirect(url_for('profile')) возвращает пользователя на страницу профиля
             после попытки загрузки, независимо от её исхода.
    """
    file = request.files["photo"]
    if file.filename == "":
        return redirect("profile")
    if not (file and allowed_file(file.filename)):
        flash({"title": "Ошибка!", "message": "Неверный файл"})
        return redirect("profile")
    if current_user.avatar:
        delete_file(current_user.avatar)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = secure_filename(f"{timestamp}_{file.filename}")
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    # Добавить путь к аватру пользователя в БД
    dataAccess.add_avatar(current_user, file_path)
    flash(
        {"title": "Успех!", "message": "Ваша картинка обновлена"},
        category="success",
    )
    return redirect(url_for("profile"))


@app.route("/horoscope/<period>")
@login_required
def horoscope(period) -> Response | str:
    """
    Views для отображения гороскопа на определенный период.

    Принимает параметр 'period', который определяет период времени для гороскопа (например, "день", "неделя").
    Перед выводом гороскопа проверяет, заполнены ли данные о дате рождения и времени рождения пользователя.
    Если данные не заполнены, отображается сообщение с просьбой их заполнить и происходит перенаправление
    на страницу профиля для дополнения информации.

    Если данные пользователя заполнены, осуществляется поиск гороскопа для данного периода и знака зодиака пользователя.
    В случае отсутствия гороскопа в базе данных, производится запрос к внешнему сервису для получения гороскопа,
    который затем сохраняется в базе данных для последующего использования.

    :param period: Строка, указывающая период гороскопа (например, "today", "week").
    :return: render_template('horoscope_chat.html') с гороскопом для заданного периода,
             или перенаправление на страницу профиля при необходимости заполнения данных.
    """
    # сделать проверку данных и перекинуть для заполнения на profile
    if not (current_user.birthday or current_user.birth_time):
        flash(
            {
                "title": "Заполните данные",
                "message": "Для создания гороскопа заполните данные",
            },
            category="error",
        )
        return redirect(url_for("profile"))

    date = date_horoscope(period)

    zodiac_sign = current_user.zodiac_sign
    # Поиск подходящего гороскопа по заданным параметрам в БД
    horoscope = dataAccess.get_horoscope(period, date, zodiac_sign)
    if not horoscope:
        get_horoscope = GetHoroscope(zodiac_sign, period)
        text = get_horoscope.get_response()
        # Добавление нового гороскопа в БД
        dataAccess.add_new_horoscope(period, zodiac_sign, text, date)
        return render_template("horoscope_chat.html", text=text)
    return render_template("horoscope_chat.html", text=horoscope.horoscope)


@app.route("/special_horoscope/", methods=["POST"])
@login_required
def special_horoscope() -> Response | str:
    """
    Views для отображения специального гороскопа на основе даты, указанной пользователем.

    POST запрос:
    Проверяет, заполнены ли дата рождения и время рождения у текущего пользователя.
    Если одно из этих данных не заполнено, выводит сообщение с просьбой заполнить данные и
    перенаправляет на страницу профиля.

    Из формы запроса извлекается специальная дата ('sp_date'), для которой должен быть создан гороскоп.
    Проверяет наличие гороскопа на эту дату в базе данных. Если гороскоп не найден, осуществляется запрос к
    внешнему сервису для получения гороскопа, который после получения сохраняется в базу данных.

    :return: render_template('horoscope_chat.html') с текстом гороскопа,
             или перенаправление на страницу профиля, если требуется заполнение данных пользователя.
    """
    # сделать проверку данных и перекинуть для заполнения на profile
    if not (current_user.birthday or current_user.birth_time):
        flash(
            {
                "title": "Заполните данные",
                "message": "Для создания гороскопа заполните данные",
            },
            category="error",
        )
        return redirect(url_for("profile"))

    form = request.form

    sp_date = form.get("sp_date")
    sp_date = datetime.strptime(sp_date, "%Y-%m-%d")
    period = "special"
    zodiac_sign = current_user.zodiac_sign
    # Поиск подходящего гороскопа по заданным параметрам в БД
    horoscope = dataAccess.get_horoscope(period, sp_date, zodiac_sign)
    if not horoscope:
        get_horoscope = GetSpecialHoroscope(sp_date, zodiac_sign)
        text = get_horoscope.get_response()
        # Добавление нового гороскопа в БД
        dataAccess.add_new_horoscope(period, zodiac_sign, text, sp_date)
        return render_template("horoscope_chat.html", text=text)
    return render_template("horoscope_chat.html", text=horoscope.horoscope)


@app.route("/natal_chart", methods=["GET", "POST"])
@login_required
def natal_chart() -> Response | str:
    """
    Views для отображения натальной карты пользователя.

    GET запрос:
    Перед отображением натальной карты проверяет, заполнены ли необходимые данные пользователя
    (дата рождения и время рождения). Если данные не заполнены, выводит сообщение с просьбой
    заполнить данные и перенаправляет на страницу профиля. В противном случае отображает страницу
    для генерации натальной карты.

    POST запрос:
    Генерирует натальную карту на основе данных пользователя, включая дату и время рождения, а также место рождения.
    Если натальная карта для пользователя уже существует в базе данных, возвращает существующую карту.
    В противном случае происходит создание новой натальной карты, которая затем сохраняется в базу данных.

    :return: при GET запросе возвращает страницу для генерации натальной карты,
             при POST запросе возвращает JSON с результатами генерации натальной карты
             (успешно создана или уже существующая карта).
    """
    if request.method == "GET":
        if not (current_user.birthday or current_user.birth_time):
            flash(
                {
                    "title": "Заполните данные",
                    "message": "Для создания гороскопа заполните данные",
                },
                category="error",
            )
            return redirect(url_for("profile"))
        return render_template("chat.html")
    # Получение натальной карты из БД текущего пользователя
    natal_cart = dataAccess.get_natal_chart(current_user.id)
    if natal_cart:
        return jsonify(
            {
                "success": True,
                "natal_chart": natal_cart.natal_chart,
            }
        )
    date = datetime.combine(current_user.birthday, current_user.birth_time)
    text = GetNatalChart2(date, current_user.city).natal_chart()
    # Добавление новой натальной карты в БД
    dataAccess.add_new_natal_cart(current_user.id, text)
    return jsonify(
        {
            "success": True,
            "natal_chart": text,
        }
    )


@app.route("/logout/")
@login_required
def logout() -> Response | str:
    """
    Views для выхода из профиля пользователя
    """
    logout_user()
    return redirect(url_for("index"))


@app.after_request
def redirect_to_sign(response):
    """
    Перехватывает ответы после обработки запросов к приложению.

    Эта функция вызывается автоматически после каждого запроса. Она проверяет статусный код ответа.
    Если статусный код ответа равен 401 (Неавторизован), происходит перенаправление пользователя на страницу
    регистрации и авторизации. Это обеспечивает, что пользователи, пытающиеся получить доступ к защищенным
    ресурсам без соответствующих прав доступа, будут направлены к форме входа, вместо отображения стандартной
    страницы с ошибкой 401.

    :param response: Объект ответа Flask, который был сгенерирован обработчиками запросов.
    :return: Исходный объект ответа или объект перенаправления на страницу авторизации.
    """
    if response.status_code == 401:
        return redirect(url_for("register_authorization"))
    return response
