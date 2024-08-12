import pymysql
import re

def generate_regex_patterns(input_string):
    patterns = []
    length = len(input_string)
    for i in range(length):
        for j in range(i + 2, length + 1):
            patterns.append(input_string[i:j])
    return "|".join(patterns)

def git_data_fining():
    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:
            query = '''
                    SELECT rd.root_url, lc.company, sr.title, sr.content, sr.id
                    FROM conn_comp_root ccr
                    JOIN conn_root_sub crs ON ccr.root_id = crs.root_id
                    JOIN conn_sub_res csr ON crs.sub_id = csr.sub_id
                    JOIN search_result sr ON csr.res_id = sr.id
                    JOIN list_company lc ON ccr.comp_id = lc.id
                    JOIN domain_root rd ON ccr.root_id = rd.id
                    WHERE tags = 'is_github'
                    UNION
                    SELECT rd.root_url, lc.company, sr.title, sr.content, sr.id
                    FROM conn_comp_root ccr
                    JOIN conn_root_res crr ON ccr.root_id = crr.root_id
                    JOIN search_result sr ON crr.res_id = sr.id
                    JOIN list_company lc ON ccr.comp_id = lc.id
                    JOIN domain_root rd ON ccr.root_id = rd.id
                    WHERE tags = 'is_github';
                    '''
            cur.execute(query)
            datas = cur.fetchall()
    
    keys = []
    for data in datas:
        key = ""
        key += data[0].split(".")[0] + "|"
        key += generate_regex_patterns(data[1])

        target = data[2] + data[3]
        l = re.search(key, target)
        if l is not None:
            keys.append(str(data[4]))

    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:
            query = 'DELETE FROM search_result WHERE tags="is_github" AND id NOT IN ({0})'.format(",".join(keys))
            cur.execute(query)
        conn.commit()
    return 0

def data_fining_seq_one():
    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:
            # 분류: filter, filter 태그가 달렸으면 필터링 당하는 대상
            query = r'''
                    UPDATE      search_result
                    SET         tags = 'filter'
                    WHERE       (url REGEXP "news|product|about|list|manual|media|magazine"
                    OR          url NOT REGEXP "\\\\")
                    AND         url REGEXP '(\/|=)[0-9a-z-]+(\.(html))*\/*$'
                    AND         tags NOT LIKE 'is_github'
                    AND         tags LIKE '';
                    '''
            cur.execute(query)

            # 분류: 파일
            query = r'''
                    INSERT INTO list_file (id, url)
                    SELECT      sr.id, sr.url
                    FROM        search_result sr
                    LEFT JOIN   list_file fl
                    ON          sr.id = fl.id
                    WHERE       sr.url REGEXP "\.(pdf|xlsx|docx|pptx|hwp|txt)+$"
                    AND         sr.tags = ''
                    AND         fl.id IS NULL;                    
                    '''
            cur.execute(query)

            # 파일 태그 업데이트
            query = r'''
                    UPDATE      search_result sr
                    JOIN        list_file fl
                    ON          sr.id = fl.id
                    SET         sr.tags = 'is_file'
                    WHERE       sr.id = fl.id;
                    '''
            cur.execute(query)
        conn.commit()
    return 0

def data_fining_seq_two():
    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:
            # 분류: 불필요한 정보 노출
            query = r'''
                    UPDATE      search_result
                    SET         tags = 'is_neednot'
                    WHERE       tags = ''
                    AND         (title REGEXP '시스템.메.지|Apache'
                    OR          url REGEXP 'editor|plugin/|namo|dext|CVS|root|[Rr]epository|changelog|jsessionid' 
                    OR          content REGEXP '시스템.메.지|워드프레스');
                    '''
            cur.execute(query)

            # 분류: 관리자 페이지
            query = r'''
                    UPDATE      search_result
                    SET         tags = 'is_admin'
                    WHERE       tags = ''
                    AND         (title REGEXP '관리자|admin'
                    OR          url REGEXP 'admin\/*$'
                    OR          content REGEXP '관리자');
                    '''
            cur.execute(query)

            # 분류: 로그인 페이지
            query = r'''
                    UPDATE      search_result
                    SET         tags = 'is_login'
                    WHERE       tags = ''
                    AND         (title REGEXP '로그인|login' 
                    OR          url REGEXP 'login\.[a-zA-Z]*$'
                    OR          content REGEXP 'login')
                    AND         url NOT REGEXP 'regist|password';
                    '''
            cur.execute(query)
        conn.commit()
    return 0

def update_filetype():
    with pymysql.connect(host='192.168.6.90', user='root', password='root', db='searchdb', charset='utf8mb4') as conn:
        with conn.cursor() as cur:
            filetypes = ["pdf", "xlsx", "docx", "pptx"]
            for filetype in filetypes:
                query = f'''
                        UPDATE  list_file
                        SET     filetype = '{0}'
                        WHERE   url REGEXP '{0}+$';
                        '''.format(filetype)
                cur.execute(query)

            query = r'''
                    UPDATE      list_file
                    SET         filetype = 'others'
                    WHERE       filetype = '';
                    '''
            cur.execute(query)
        conn.commit()
    return 0

def run():
    
    data_fining_seq_one()
    update_filetype()
    data_fining_seq_two()

    return 0