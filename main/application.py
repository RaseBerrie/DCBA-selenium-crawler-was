from main import *
from functions.database.utils import database_query
from functions.crawler.module import process_start
from functions.crawler.dbbuilder import dbbuild_module, conn_root_sub

import io, psutil, re, pymysql
import json
import csv

from urllib.parse import quote, unquote
from flask import Blueprint, render_template, make_response, request

crawler = Blueprint('crawler', __name__, template_folder='templates/crawler', url_prefix="/crawler")

####################    함수 정의       ####################

def new_csv_list(file_storage):
    result = []
    with io.StringIO(file_storage.read().decode('utf-8-sig')) as file:
        file.seek(0)
        reader = csv.reader(file)
        for line in reader:
            result.append(line[0])
    return result

def find_process():
    for proc in psutil.process_iter(['name']):
        if proc.info["name"] == "chromedriver.exe":
            return True
    return False

def check_url(text:str):
    url_reg = r"[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
    reg = re.compile(url_reg)
    res = reg.search(text)

    if res == None:
        return False
    else:        
        return True

####################    접속 직후       ####################

@crawler.route('/')
def crawler_page():
    cookie = json.loads(unquote(request.cookies.get("status")))
    if cookie["crawler"] != False:
        if find_process():
            return render_template('crawler_inprocess.html', processing=False)
        else:
            return render_template('crawler_finish.html', processing=False)
    else:
        return render_template('crawler_start.html', reload=False)

####################    키 리스트 보기  ####################

@crawler.route('/table')
def reload():
    query = "SELECT company, search_key, bing, google, github_bing, github_google FROM search_key ORDER BY id DESC"
    datas = database_query(query)

    return render_template('tab_one.html', datas=datas)

####################    크롤러 시작     ####################

@crawler.route('/start')
def start():
    cookie = json.loads(unquote(request.cookies.get("status")))
    args = dict()

    args["google"] = False
    args["bing"] = True
    args["github_google"] = False
    args["github_bing"] = True

    json_val = json.dumps(args)
    process_start(json_val)

    resp = make_response(render_template('crawler_inprocess.html', processing=True))
    cookie["crawler"] = True

    resp.set_cookie("status", quote(json.dumps(cookie)), path='/')
    return resp

####################    링크 추가       ####################

@crawler.route('/addlinks', methods=['GET', 'POST'])
def addlinks():
    result = dict()
    if request.method == 'GET':
        comp = request.args.get("comp")
        data = request.args.get("data")

        result_data = []
        data_list = data.split(",")
        for text in data_list:
            text = text.strip()
            if check_url(text):
                result_data.append(text)

        result[comp] = result_data

    else:
        comp = request.form['comp']
        data = request.files['data']

        result_data = []
        data_list = new_csv_list(data)
        for text in data_list:
            if check_url(text):
                result_data.append(text)

        result[comp] = result_data

    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:
            for key in result[comp]:
                query = 'INSERT IGNORE INTO search_key(company, search_key) VALUES("{0}", "{1}")'.format(comp, key)
                cur.execute(query)
            conn.commit()

    # 서브도메인 리스트에 키 집어넣기
    dbbuild_module()

    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:
            for key in result[comp]:
                query = 'INSERT IGNORE INTO list_company(company) VALUES("{0}")'.format(comp)
                cur.execute(query)
            conn.commit()

            query = 'SELECT id FROM list_company WHERE company = "{0}"'.format(comp)
            comp_id = database_query(query)

    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:            
            query = '''SELECT rd.id FROM domain_root rd
                    LEFT JOIN conn_comp_root ccr ON rd.id = ccr.root_id
                    WHERE ccr.comp_id IS NULL'''
            ids = database_query(query)

            if str(type(ids)) != "<class 'int'>":
                for id in ids:
                    query = 'INSERT INTO conn_comp_root(comp_id, root_id) VALUES({0}, {1})'.format(comp_id[0][0], id[0])
                    cur.execute(query)
                conn.commit()
            else:
                query = 'INSERT INTO conn_comp_root(comp_id, root_id) VALUES({0}, {1})'.format(comp_id[0][0], ids[0][0])
                print(query)
                cur.execute(query)
                conn.commit()

            conn_root_sub(cur)

    return result

