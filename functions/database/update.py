import functions.database.insert as insert
import functions.database.utils as utils

# comp_label을 넣으면 company id를 돌려줌
def company_id(comp_label):
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                        INSERT IGNORE INTO res_data_label(label)
                        VALUE("''' + comp_label + '");')
            conn.commit()

            cur.execute('SELECT id FROM res_data_label WHERE label="' + comp_label + '";')
            id = cur.fetchone()

    return id[0]

# domain을 넣으면 rootdomain으로 바꿔 줌
def rootdomain(domain):
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

# 루트 키와 회사 번호를 연결함
def data_labels(comp_id, url_list):
    root_url_set = set()
    sub_url_set = set()

    # URL(키)-데이터베이스 아이디(값) 연결
    root_key_id_dict = dict()
    sub_key_id_dict = dict()

    # 서브 도메인(키)-루트 도메인(값) 연결
    id_pair = dict()

    sub_url_set.update(url_list)
    for url in url_list:
        id_pair[url] = rootdomain(url)
        root_url_set.add(id_pair[url])
    
    sub_url_set = sub_url_set - root_url_set

    conn = utils.database_connect()
    cur = conn.cursor()

    # conn_comp_root
    for root_url in list(root_url_set):

        # 루트도메인 label에 삽입
        cur.execute(f'INSERT IGNORE INTO res_data_label(label) VALUE("{root_url}")')
        conn.commit()

        # 루트도메인 id 찾기
        cur.execute(f'SELECT id FROM res_data_label WHERE label = ("{root_url}")')
        id = cur.fetchone()

        # 루트도메인을 Key 로 해서 Dict에서 id를 검색할 수 있음
        root_key_id_dict[root_url] = id[0]

        # 루트도메인과 회사를 연결
        insert.into_tree(id[0], comp_id)
        insert.rootdomain(id[0], root_url)

    # conn_root_sub
    for sub_url in list(sub_url_set):
        # 이 서브도메인에 해당되는 루트도메인을 찾음
        this_root_url = id_pair[sub_url]
        this_root_id = root_key_id_dict[this_root_url]

        # 서브도메인 label에 삽입
        cur.execute(f'INSERT IGNORE INTO res_data_label(label) VALUE("{sub_url}")')
        conn.commit()

        # 서브도메인 id 찾기
        cur.execute(f'SELECT id FROM res_data_label WHERE label = ("{sub_url}")')
        id = cur.fetchone()

        # 서브도메인을 Key 로 해서 Dict에서 id를 검색할 수 있음
        sub_key_id_dict[sub_url] = id[0]

        # 서브도메인과 루트도메인을 연결
        insert.into_tree(id[0], this_root_id)
        insert.subdomain(id[0], sub_url)

    cur.close()
    conn.close()

    return 0

# 중복되지 않는 서브도메인 값 추출
def sub_keys(query):
    conn = utils.database_connect()
    cur = conn.cursor()

    url_list = list()
    
    # 검색 결과에서 추출 시 반드시 이미 키에 존재하는 값을 포함함
    # → 키에 없는/루트 도메인에 없는 값은 존재하지 않음
    #
    # ∴ 추가로 있을 수 있는 서브도메인 찾기 목적
    
    cur.execute(r"SELECT DISTINCT subdomain FROM res_data_content WHERE url LIKE '%" + query + r"%'")
    datas = cur.fetchall()

    return url_list