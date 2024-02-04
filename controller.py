from flask import render_template, Response, redirect, url_for
from flask_login import login_required, logout_user

from app import app


@app.route('/')
@app.route('/index/')
def index() -> Response | str:
    """
        Views для главной страницы.
    """
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register() -> Response | str:
    """
        Views для страницы регистрации пользователя.
    """
    return render_template('register.html')


@app.route('/authorization', methods=['GET', 'POST'])
def authorization() -> Response | str:
    """
        Views для страницы авторизации пользователя.
    """
    return render_template('authorization.html')


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