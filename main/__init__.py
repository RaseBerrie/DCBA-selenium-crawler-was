from flask import Flask
from flask_restx import Api

app = Flask(__name__)
api = Api(app)

from main.crawler import crawler
from main.keys import keys

api.add_namespace(crawler)
api.add_namespace(keys)