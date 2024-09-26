from main import *
from functions.crawler.processor import process_start
from functions.database.utils import insert_into_keys, create_task_list

import json, io, re, csv

from flask import request, jsonify
from flask_restx import Resource, Namespace

crawler = Namespace('crawler')
key_dict = dict()

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

@crawler.route('/run')
class StartCrawler(Resource):
    def get(self):
        args = json.loads(request.args.get('args'))

        for key in args.keys():
            if args[key]:
                ls = create_task_list(key)
                key_dict[key] = ls
            else: key_dict[key] = list()

        try:
            process_start(args, key_dict)
            return jsonify({"status": "success"})
        
        except Exception as e:
            print(e)
            return jsonify({"status": "fail"})
    
@crawler.route('/keys')
class KeyControl(Resource):
    def get(self):
        comp = request.args.get('comp')
        data = request.args.get('data')

        keys = []
        data_list = data.split("\n")
        for text in data_list:
            text = text.strip()
            if check_url(text):
                keys.append(text)

        insert_into_keys(comp, keys)
        return jsonify({"comp": comp, "data": keys})
        
    def post(self):
        comp = request.form['comp']
        data = request.files['data']

        keys = []
        data_list = new_csv_list(data)
        for text in data_list:
            if check_url(text):
                keys.append(text)

        insert_into_keys(comp, keys)
        return jsonify({"comp": comp, "data": keys})