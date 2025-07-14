from flask import Flask, session
from flask_session import Session

def createApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "hadfhdfadfj"

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024

    from .routes import routes

    app.register_blueprint(routes, url_prefix="/")

    return app