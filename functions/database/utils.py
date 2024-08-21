import pymysql

def database_connect():
    conn = pymysql.connect(host='192.168.6.90',
                           user='root',
                           password='root',
                           db='searchdb',
                           charset='utf8mb4')
    return conn

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

def save_to_database(se, sd, title, link, content, target):
    if "bing" in link: return 0

    with database_connect() as conn:
        with conn.cursor() as cur:
            query = 'INSERT IGNORE INTO res_data_label (label) VALUE ("{0}")'.format(link)
            cur.execute(query)
            conn.commit()
            
            line = sd
            if ":" in line: line = line.split(":")[0]

            query = '''
                    INSERT IGNORE INTO res_data_content
                    (searchengine, subdomain, res_title, res_url, res_content, tags)
                    VALUES('{0}', '{1}', '{2}', '{3}', '{4}', 
                    '''.format(se, line, title, link, content)
            
            if target == "github":
                query = query + "'git');"
            else:
                query = query + "'');"

            cur.execute(query)
            conn.commit()
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