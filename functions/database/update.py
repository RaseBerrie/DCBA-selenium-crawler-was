import functions.database.insert as insert
import functions.database.utils as utils

def select_auto_increment(cur):
    query = ''' 
        SELECT AUTO_INCREMENT
        FROM information_schema.tables
        WHERE table_name = 'res_data_label';
        '''
    cur.execute(query)
    id = cur.fetchone()

    return id

def company(comp_label):
    with utils.database_connect() as conn:
        with conn.cursor as cur:
            cur.execute('''
                        INSERT IGNORE INTO res_data_label(label)
                        VALUE("''' + comp_label + '");')
            conn.commit()

            cur.execute('SELECT id FROM res_data_label WHERE label="' + comp_label + '";')
            id = cur.fetchone()

    return id

def rootdomain(domain):
    if ":" in domain: tmp = domain.split(":")
    domain = tmp[0] # 포트 번호 삭제

    found = 0
    tmp = domain.split(".")

    if tmp.count('com') == 1: found = tmp.index('com')

    elif (tmp.count('kr') == 1):
        if tmp.count('or') == 1: found = tmp.index('or')
        elif tmp.count('co') == 1: found = tmp.index('co')
        else: found = tmp.index('kr')

    elif tmp.count('jp') == 1: found = tmp.index('jp')

    elif tmp.count('net') == 1: found = tmp.index('net')

    elif ((tmp.count('co') == 1) and (tmp.count('uk') == 1)): found = tmp.index('co')

    elif tmp.count('ca') == 1: found = tmp.index('ca')

    elif tmp.count('uz') == 1: found = tmp.index('uz')

    elif tmp.count('in') == 1: found = tmp.index('in')

    elif tmp.count('cn') == 1: found = tmp.index('cn')

    elif ((tmp.count('co') == 1) and (tmp.count('uk') == 1)): found = tmp.index('co')

    found = found - 1
    tmp_list = tmp[found:]

    result = ".".join(tmp_list)
    return result

def root_keys(comp_id, key_list):
    root_key_set = set()

    for key in key_list:
        root_key_set.update(rootdomain(key))
    
    root_key_list = list(root_key_set)
    root_key_dict = dict()

    conn = utils.database_connect()
    cur = conn.cursor()

    id = select_auto_increment(cur)
    for i, key in enumerate(root_key_list):
        cur.execute('INSERT INTO res_data_label(label) VALUE("' + key + '")')
        conn.commit()

        insert.into_tree(id + i, comp_id)
        root_key_dict[key] = id + i

    cur.close()
    conn.close()

    # root_key_dict를 반환
    # → ancestor의 id를 확인한 후 subdomain으로 넘어감
    return root_key_dict

def sub_keys(root_key_dict):
    return 0