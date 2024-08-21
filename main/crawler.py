from main import *
from functions.crawler.processor import process_start

import json

from flask import request, jsonify
from flask_restx import Resource, Namespace

crawler = Namespace('crawler')

@crawler.route('/')
class StartCrawler(Resource):
    def get(self):
        callback = request.args.get('callback')
        args = json.loads(request.args.get('args'))
        
        process_start(args)
        response_data = {"status": "success"}
        
        # JSONP 응답을 처리하는 부분
        if callback:
            response = app.response_class(
                response=f"{callback}({jsonify(response_data).data.decode('utf-8')})",
                status=200,
                mimetype='application/javascript'
            )
        else: response = jsonify(response_data)
        
        return response