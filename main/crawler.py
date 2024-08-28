from main import *
from functions.crawler.processor import process_start

import json, io, re, csv

from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace

crawler = Namespace('crawler')

def new_csv_list(file_storage):
    result = []
    with io.StringIO(file_storage.read().decode('utf-8-sig')) as file:
        file.seek(0)
        reader = csv.reader(file)
        for line in reader:
            result.append(line[0])
    return result

def check_url(text:str):
    url_reg = r"[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
    reg = re.compile(url_reg)
    res = reg.search(text)

    if res == None:
        return False
    else:        
        return True

def new_response(json_string):
    response = make_response(json_string)
    response.headers.add('Access-Control-Allow-Origin', "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")

    return response

@crawler.route('/run')
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
    
@crawler.route('/keys')
class KeyControl(Resource):
    def get(self):
        comp = request.args.get('comp')
        data = request.args.get('data')

        keys = []
        data_list = data.split(",")
        for text in data_list:
            text = text.strip()
            if check_url(text):
                keys.append(text)

        response = new_response(jsonify({"comp": comp, "data": keys}))
        return response
        
    def post(self):
        comp = request.form['comp']
        data = request.files['data']

        keys = []
        data_list = new_csv_list(data)
        for text in data_list:
            if check_url(text):
                keys.append(text)

        response = new_response(jsonify({"comp": comp, "data": keys}))
        return response
