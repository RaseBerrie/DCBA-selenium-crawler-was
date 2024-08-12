import utils

def into_root(id):
    conn = utils.database_connect()
    cur = conn.cursor()

    ROOT_QUERY = 'INSERT INTO res_closure VALUES ({0}, {0}, 0);'

    cur.execute(ROOT_QUERY.format(id))
    conn.commit()

def into_tree():
    conn = utils.database_connect()
    cur = conn.cursor()

    TREE_QUERY = 'CALL insertData({1}, {0})'

    cur.execute(query)
    datas = cur.fetchall()
    
    for data in datas:
        try:
            query = TREE_QUERY.format(data[0], data[1])
            cur.execute(query)
            conn.commit()

            print(query)
        except:
            conn.rollback()