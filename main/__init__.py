from flask import Flask
from flask_restx import Api

def create_app():
    app = Flask(__name__)
    api = Api(app)

    from main.crawler import crawler
    from main.data import data

    api.add_namespace(crawler)
    api.add_namespace(data)

    return app