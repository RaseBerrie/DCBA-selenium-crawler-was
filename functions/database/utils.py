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
            
            root_keys = list(root_key_set)
            for root_key in root_keys:
                query = f"INSERT IGNORE INTO list_rootdomain(company, url) VALUE('{comp}', '{root_key}')"
                cur.execute(query)

                query = f"INSERT IGNORE INTO list_subdomain(rootdomain, url, is_root) VALUE('{root_key}', '{root_key}', 1)"
                cur.execute(query)

                for key in keys:
                    if key not in root_key:
                        query = f"INSERT IGNORE INTO list_subdomain(rootdomain, url, is_root) VALUE('{root_key}', '{key}', 0)"
                        cur.execute(query)
                    else: continue

                    query = f"INSERT IGNORE INTO req_keys(req_keys.key) VALUE('{key}')"
                    cur.execute(query)

            conn.commit()
            return 0

def create_task_list(task):
    task_list = []
    with database_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT req.key FROM req_keys req WHERE {0}='notstarted' and id > 1000".format(task))
            keys = cur.fetchmany(36)
            
            for key in keys:
                task_list.append(key[0])
            
            for task_url in task_list:
                cur.execute("UPDATE req_keys SET {0} = 'processing' WHERE req_keys.key = '{1}'".format(task, task_url))
                cur.execute("UPDATE req_keys SET {0}_status = 'running' WHERE req_keys.key = '{1}'".format(task, task_url))
            
            conn.commit()
    return task_list

def save_to_database(se, sd, title, link, content,
                     git=False, original_url=None, cached_data=None):
    
    if "bing" in link or "github" in sd:
        return 0

    with database_connect() as conn:
        with conn.cursor() as cur:
            subdomain = sd
            if ":" in subdomain: subdomain = subdomain.split(":")[0]

            if git: query = 'INSERT INTO res_data_git'
            else: query = 'INSERT INTO res_data_def'

            query = query + '''
                    (searchengine, subdomain, res_title, res_url, res_content)
                    VALUES('{0}', '{1}', '{2}', '{3}', '{4}'); 
                    '''.format(se, subdomain, title, link, content)
            
            try:
                cur.execute(query)
            except pymysql.MySQLError as e:
                error_code, error_message = e.args

                if error_code == 1062: pass
                elif error_code == 1452:
                    rootdomain = find_rootdomain(subdomain)
                    query_sub = f'''INSERT INTO list_subdomain (rootdomain, url, is_root)
                    VALUES("{rootdomain}", "{subdomain}", '''

                    if rootdomain == subdomain: query_sub += "1)"
                    else: query_sub += "0)"

                    try:
                        cur.execute(query_sub)
                        cur.execute(query)
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
                else:
                    raise ValueError(f"{error_message}")
                
            if cached_data is not None:
                query = "INSERT IGNORE INTO res_data_cache (url, cache) VALUES (%s, %s)"
                cur.execute(query, (link, cached_data, ))

            conn.commit()
    return 0

def update_status(se, url, status, git=False):
    with database_connect() as conn:
        with conn.cursor() as cur:
            if git: column = se + '_git'
            else: column = se + '_def'
                    
            query = 'UPDATE req_keys req SET ' + column + ' = "' + status + '" WHERE req.key = "' + url + '";'
            cur.execute(query)

            if status == 'notstarted':
                query = 'UPDATE req_keys req SET ' + column + '_status = "killed" WHERE req.key = "' + url + '";'
            elif status == 'finished':
                query = 'UPDATE req_keys req SET ' + column + '_status = "done" WHERE req.key = "' + url + '";'

            cur.execute(query)
        conn.commit()
    return 0