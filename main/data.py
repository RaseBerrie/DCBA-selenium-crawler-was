from main import *
from functions.database import datafine
from functions.parser import pdf

from flask import jsonify
from flask_restx import Resource, Namespace

data = Namespace('data')

@data.route('/classify')
class DataClassify(Resource):
    def get(self):
        try:
            datafine.run()
            response_data = {"status": "success"}
        except Exception as e:
            print(e)
            response_data = {"status": "errored"}

        response = jsonify(response_data)
        return response

@data.route('/file')
class FileControl(Resource):
    def get(self):
        try:
            pdf.run()
            response_data = {"status": "success"}
        except Exception as e:
            print(e)
            response_data = {"status": "errored"}

        response = jsonify(response_data)
        return response