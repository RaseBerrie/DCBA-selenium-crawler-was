import re

def generate_regex_patterns(input_string):
    patterns = []
    length = len(input_string)
    for i in range(length):
        for j in range(i + 2, length + 1):
            patterns.append(input_string[i:j])
    return "|".join(patterns)

def filter_github(cur):
    query = '''
    SELECT root.company, root.url, data.id, data.res_title, data.res_content
    FROM res_data_git data
    JOIN list_subdomain sub ON data.subdomain = sub.url
    JOIN list_rootdomain root ON sub.rootdomain = root.url
    '''
    cur.execute(query)
    datas = cur.fetchall()

    keys = set()
    for data in datas:
        key = ""
        key += data[1].split(".")[0] + "|"
        key += generate_regex_patterns(data[0])

        target = data[3] + data[4]
        l = re.search(key, target)
        if l is not None:
            keys.add(str(data[2]))

    query = 'DELETE FROM res_data_git WHERE id NOT IN ({0})'.format(",".join(list(keys)))
    return query

def is_admin(cur):
    query = 'select res_title, id from res_data_def where res_title regexp "관리" and tags = ""'
    cur.execute(query)
    datas = cur.fetchall()

    id_list = ""
    for data in datas:
        res_title = data[0]

        res_title_front = res_title.split("관리")[0]
        try: res_title_end = res_title.split("관리")[1]
        except: res_title_end = ""

        fined_front = res_title_front.split(" ")[-1]
        if fined_front == "":
            try:
                fined_front = res_title_front.split(" ")[-2]
            except:
                pass

        fined_end = res_title_end.split(" ")[0]
        if fined_end == "":
            try:
                fined_end = res_title_end.split(" ")[1]
            except:
                pass

        if "페이지" in fined_end or '시스템' in fined_end:
            id_list = id_list + str(data[1]) + ", "
    
    if len(id_list) > 0:
        query = "UPDATE res_data_def SET tags = 'admin' WHERE id in (" + id_list[:-2] + ")"
    else:
        query = None
        
    return query