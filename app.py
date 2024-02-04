import uuid

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_toastr import Toastr

app = Flask(__name__)

if __name__ == "__main__":
    app.run()