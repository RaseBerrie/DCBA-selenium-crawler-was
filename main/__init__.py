from flask import Flask
DCBA_API = Flask(__name__)

from main.application import crawler
DCBA_API.register_blueprint(crawler)