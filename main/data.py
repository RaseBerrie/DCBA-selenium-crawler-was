from main import *
from functions.database import classify
from functions.parser.pdf import pdf_settitle

from flask import request, jsonify
from flask_restx import Resource, Namespace

data = Namespace('data')

@data.route('/classify')
class DataClassify(Resource):
    def get(self):
        callback = request.args.get('callback')
        try:
            classify.run()
            response_data = {"status": "success"}
        except:
            response_data = {"status": "errored"}

        # JSONP 응답을 처리하는 부분
        if callback:
            response = app.response_class(
                response=f"{callback}({jsonify(response_data).data.decode('utf-8')})",
                status=200,
                mimetype='application/javascript'
            )
        else: response = jsonify(response_data)
        return response

@data.route('/file')
class FileControl(Resource):
    def get(self):
        callback = request.args.get('callback')
        try:
            pdf_settitle()
            response_data = {"status": "success"}
        except:
            response_data = {"status": "errored"}

        if callback:
            response = app.response_class(
                response=f"{callback}({jsonify(response_data).data.decode('utf-8')})",
                status=200,
                mimetype='application/javascript'
            )
        else: response = jsonify(response_data)
        return response