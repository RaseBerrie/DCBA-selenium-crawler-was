import pymysql, logging

logging.basicConfig(filename='C:\\Users\\itf\\Documents\\selenium-search-api\\logs\\crawler_error.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

def database_connect():
    conn = pymysql.connect(host='192.168.6.90',
                           user='root',
                           password='root',
                           db='searchdb',
                           charset='utf8mb4')
    return conn

def find_rootdomain(domain):
    if ":" in domain:
        tmp = domain.split(":")
        domain = tmp[0] # 포트 번호 삭제

    found = 0
    tmp = domain.split(".")

    tld = tmp[-1]
    second_level = tmp[-2] if len(tmp) > 1 else ''

    if tld in ['com', 'jp', 'net', 'ca', 'uz', 'in', 'cn']:
        found = tmp.index(tld)
    elif tld == 'kr':
        found = tmp.index(second_level if second_level in ['or', 'co', 'ac'] else tld)
    elif tld == 'co' and second_level == 'uk':
        found = tmp.index('co')

    found = found - 1
    tmp_list = tmp[found:]

    result = ".".join(tmp_list)
    return result

def insert_into_keys(comp, keys):
    root_key_set = set()
    with database_connect() as conn:
        with conn.cursor() as cur:
            query = f"INSERT IGNORE INTO list_company(company) VALUE('{comp}')"
            cur.execute(query)
            
            for key in keys:
                root_key_set.add(find_rootdomain(key))

                query = f"INSERT IGNORE INTO req_keys(req_keys.key) VALUE('{key}')"
                cur.execute(query)
            
            root_keys = list(root_key_set)
            for root_key in root_keys:
                query = f"INSERT IGNORE INTO list_rootdomain(company, url) VALUE('{comp}', '{root_key}')"
                cur.execute(query)

                query = f"INSERT IGNORE INTO list_subdomain(rootdomain, url, is_root) VALUE('{root_key}', '{root_key}', 1)"
                cur.execute(query)

                for key in keys:
                    if key in root_key:
                        query = f"INSERT IGNORE INTO list_subdomain(rootdomain, url, is_root) VALUE('{root_key}', '{key}', 0)"
                        cur.execute(query)
                    else: continue

            conn.commit()
            return 0

def create_task_list(task):
    task_list = []
    with database_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT req.key FROM req_keys req WHERE {0}='notstarted' and id > 1374".format(task))
            keys = cur.fetchmany(36)
            
            for key in keys:
                task_list.append(key[0])
            
            for task_url in task_list:
                cur.execute("UPDATE req_keys SET {0} = 'processing' WHERE req_keys.key = '{1}'".format(task, task_url))
            
            conn.commit()
    return task_list

def save_to_database(se, sd, title, link, content,
                     git=False, original_url=None):
    
    if "bing" in link or "github" in sd:
        return 0

    with database_connect() as conn:
        with conn.cursor() as cur:
            subdomain = sd
            if ":" in subdomain: subdomain = subdomain.split(":")[0]

            if git : query = 'INSERT INTO res_data_git'
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

                    try:
                        cur.execute(query_sub)
                        cur.execute(query)
                        
                        conn.commit()
                    except:
                        query_find_comp = f'''SELECT company FROM req_keys req 
                        JOIN list_subdomain sub ON sub.url = req.key
                        JOIN list_rootdomain root ON root.url = sub.rootdomain
                        WHERE req.key = "{original_url}"'''
                        cur.execute(query_find_comp)

                        company = cur.fetchone()
                        query_root = f'''INSERT INTO list_rootdomain (company, url)
                        VALUES ("{company[0]}", "{rootdomain}")'''
                        
                        cur.execute(query_root)
                        cur.execute(query_sub)
                        cur.execute(query)

                        conn.commit()
                else:
                    logging.error(query) #→ 로깅 후 계속 진행
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