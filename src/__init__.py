from flask import Flask, session
from flask_session import Session

def createApp():
    app = Flask(__name__)
    app.secret_key = "e21d3fbb30f3bbb8ac5652c137a6a216db3085e4ff12a4d69e5114"

    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024

    from .routes import routes

    app.register_blueprint(routes, url_prefix="/")

    return app