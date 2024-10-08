from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from functions.database import *

db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/searchdb'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800
    }
    
    from main.crawler import crawler
    from main.data import data

    api = Api(app)
    api.add_namespace(crawler)
    api.add_namespace(data)

    db.init_app(app)
    
    return app