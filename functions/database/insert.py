import functions.database.utils as utils

def into_root(id):
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            ROOT_QUERY = 'INSERT INTO res_closure VALUES ({0}, {0}, 0);'
            
            cur.execute(ROOT_QUERY.format(id))
            conn.commit()

def into_tree(id, parent_id):
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            TREE_QUERY = 'CALL insertData({0}, {1})'

            try:
                cur.execute(TREE_QUERY.format(id, parent_id))
                conn.commit()
            except:
                conn.rollback()

def subdomain(id, url):
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            query = f"INSERT IGNORE INTO list_subdomain(id, url) VALUE({id}, '{url}')"
            cur.execute(query)        

        conn.commit()
        return 0

def rootdomain(id, url):
    with utils.database_connect() as conn:
        with conn.cursor() as cur:
            query = f"INSERT IGNORE INTO list_rootdomain(id, url) VALUE({id}, '{url}')"
            cur.execute(query)        
    
        conn.commit()
        return 0
