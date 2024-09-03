import functions.database.utils as utils
import re

def generate_regex_patterns(input_string):
    patterns = []
    length = len(input_string)
    for i in range(length):
        for j in range(i + 2, length + 1):
            patterns.append(input_string[i:j])
    return "|".join(patterns)

def git_data_fining():
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
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

    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            query = 'DELETE FROM res_data_git WHERE id NOT IN ({0})'.format(",".join(list(keys)))
            cur.execute(query)

        conn.commit()
        return 0

def data_fining_seq_one():
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            # 분류: 퍼블릭 (일반적으로 공개할 수 있는 내용)
            query = r'''
            UPDATE  res_data_def
            SET     tags = 'public'
            WHERE   tags LIKE ''
            AND     (res_url REGEXP "/[0-9]+/|[0-9]+$|notice_?view|/post/"
            OR      res_url REGEXP '(\/|=)[0-9a-z-]+(\.(html))*\/*$')
            AND     res_url NOT LIKE '%download%'
            '''
            cur.execute(query)
 
            # 분류: 파일
            query = r'''
            UPDATE  res_data_def
            SET     tags = 'file'
            WHERE   res_url REGEXP "\\.(pdf|xlsx|docx|ppt[x]{0,1}|hwp|txt|ai)+$"
            AND     tags = ''
            '''
            cur.execute(query)
 
            # 파일 태그 업데이트
            query = r'''
            INSERT IGNORE INTO res_tags_file (id, url)
            (SELECT id, res_url FROM res_data
            WHERE tags = 'file')
            '''
            cur.execute(query)
        
        conn.commit()
        return 0

def data_fining_seq_two():
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            # 분류: 불필요한 정보 노출
            query = r'''
            UPDATE  res_data_def
            SET     tags = 'expose'
            WHERE   tags = ''
            AND     (res_title REGEXP '시스템.메.지|Apache'
            OR      res_url REGEXP 'editor|plugin/|namo|dext|CVS|root|[Rr]epository|changelog|jsessionid'
            OR      res_content REGEXP '시스템.메.지|워드프레스');
            '''
            cur.execute(query)
            
            # 분류: 관리자 페이지
            query = r'''
            UPDATE      res_data_def
            SET         tags = 'admin'
            WHERE       tags = ''
            AND         (res_title REGEXP '관리자|admin'
            OR          res_url REGEXP 'admin\/*$'
            OR          res_content REGEXP '관리자');
            '''
            cur.execute(query)
            
            # 분류: 로그인 페이지
            query = r'''
            UPDATE  res_data_def
            SET     tags = 'login'
            WHERE   tags = ''
            AND     (res_title REGEXP '로그인|login' 
            OR      res_url REGEXP 'login\.[a-zA-Z]*$'
            OR      res_content REGEXP 'login')
            AND     res_url NOT REGEXP 'regist|password';
            '''
            cur.execute(query)

        conn.commit()
        return 0

def update_filetype():
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            filetypes = ["pdf", "xlsx", "docx", "pptx"]
            for filetype in filetypes:
                query = '''
                UPDATE  res_tags_file
                SET     filetype = '{0}'
                WHERE   url REGEXP '{0}+$';
                '''.format(filetype)
                cur.execute(query)
                
            query = r'''
            UPDATE  res_tags_file
            SET     filetype = 'pptx'
            WHERE   url REGEXP 'ppt+$';
            '''
            cur.execute(query)
            
            query = r'''
            UPDATE      res_tags_file
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
