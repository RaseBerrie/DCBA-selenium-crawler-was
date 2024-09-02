import pymysql

def find_rootdomain(domain):
    if ":" in domain:
        tmp = domain.split(":")
        domain = tmp[0] # 포트 번호 삭제

    found = 0
    tmp = domain.split(".")

    if tmp[-1] == 'com': found = tmp.index('com')

    elif tmp[-1] == 'kr':
        if tmp[-2] == 'or': found = tmp.index('or')
        elif tmp[-2] == 'co': found = tmp.index('co')
        elif tmp[-2] == 'ac': found = tmp.index('ac')
        else: found = tmp.index('kr')

    elif tmp[-1] == 'jp' == 1: found = tmp.index('jp')

    elif tmp[-1] == 'net' == 1: found = tmp.index('net')

    elif ((tmp[-1] == 'co') and (tmp[-2] == 'uk')): found = tmp.index('co')

    elif tmp[-1] == 'ca': found = tmp.index('ca')

    elif tmp[-1] == 'uz': found = tmp.index('uz')

    elif tmp[-1] == 'in': found = tmp.index('in')

    elif tmp[-1] == 'cn': found = tmp.index('cn')

    elif ((tmp[-1] == 'co') and (tmp[-2] == 'uk')): found = tmp.index('co')

    found = found - 1
    tmp_list = tmp[found:]

    result = ".".join(tmp_list)
    return result

def database_connect():
    conn = pymysql.connect(host='192.168.6.90',
                           user='root',
                           password='root',
                           db='searchdb',
                           charset='utf8mb4')
    return conn

def insert_into_keys(comp, keys):
    root_key_set = set()
    with database_connect() as conn:
        with conn.cursor() as cur:
            query = f"INSERT INTO list_company(company) VALUE('{comp}')"
            cur.execute(query)
            conn.commit()
            
            for key in keys:
                root_key_set.add(find_rootdomain(key))
            
            root_keys = list(root_key_set)
            for root_key in root_keys:
                query = f"INSERT INTO list_rootdomain(company, url) VALUE('{comp}', '{root_key}')"
                cur.execute(query)

                query = f"INSERT INTO list_subdomain(rootdomain, url, is_root) VALUE('{root_key}', '{root_key}', 1)"
                cur.execute(query)
            conn.commit()

            for key in keys:
                query = f"INSERT IGNORE INTO list_subdomain(rootdomain, url, is_root) VALUE('{root_key}', '{key}', 0)"
                cur.execute(query)
            conn.commit()

            for key in keys:
                query = f"INSERT INTO req_keys(req_keys.key) VALUE('{key}')"
                cur.execute(query)
            conn.commit()

    return 0

def create_task_list(task):
    task_list = []
    with database_connect() as conn:
        with conn.cursor() as cur:
            url = cur.execute("SELECT req.key FROM req_keys req WHERE {0}='notstarted'".format(task))

            while url:
                if str(type(url)) == "<class 'tuple'>":
                    task_list.append(url[0])
                url = cur.fetchone()

    return task_list

def save_to_database(se, sd, title, link, content, isgit):
    if "bing" in link: return 0

    with database_connect() as conn:
        with conn.cursor() as cur:
            subdomain = sd
            if ":" in subdomain: subdomain = subdomain.split(":")[0]

            if isgit : query = 'INSERT INTO res_data_git'
            else: query = 'INSERT INTO res_data_def'

            query = query + '''
                    (searchengine, subdomain, res_title, res_url, res_content)
                    VALUES('{0}', '{1}', '{2}', '{3}', '{4}'); 
                    '''.format(se, subdomain, title, link, content)
            
            try:
                cur.execute(query)
                conn.commit()

            except pymysql.MySQLError as e:
                error_code, error_message = e.args
                if error_code == 1062:
                    pass

                elif error_code == 1452:
                    rootdomain = find_rootdomain(subdomain)
                    query_sub = f'''INSERT INTO list_subdomain (rootdomain, url, is_root)
                    VALUES("{rootdomain}", "{subdomain}", '''

                    if rootdomain == subdomain: query_sub += "1)"
                    else: query_sub += "0)"

                    cur.execute(query_sub)
                    conn.commit()

                    cur.execute(query)
                    conn.commit()

                else:
                    print("ERROR: Error occured in save_to_database() query")
                    pass
    return 0

def update_status(se, url, status, git=False):
    with database_connect() as conn:
        with conn.cursor() as cur:
            query = 'UPDATE req_keys req SET ' + se + '_'
            if git:
                    query += 'git'
            else:
                    query += 'def'
            query += '= "' + status + '" '
            query += 'WHERE req.key = "' + url + '";'
            cur.execute(query)
        conn.commit()
    return 0