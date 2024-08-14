from main import *

import re, io, csv
import functions.database.update as update

from flask import request
from flask_restx import Resource, Namespace

keys = Namespace('keys')

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

@keys.route('/')
class KeyControl(Resource):
    def get(self):
        comp = request.args.get("comp")
        data = request.args.get("data")

        keys = []
        data_list = data.split(",")
        for text in data_list:
            text = text.strip()
            if check_url(text):
                keys.append(text)

        comp_id = update.company(comp)
        root_key_dict = update.root_keys(comp_id, keys)
        update.sub_keys(root_key_dict)

        return {comp: keys}
        
    def post(self):
        comp = request.form['comp']
        data = request.files['data']

        result_data = []
        data_list = new_csv_list(data)
        for text in data_list:
            if check_url(text):
                result_data.append(text)

        return {comp: result_data}
