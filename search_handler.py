
import cs304dbi as dbi

def searchByPosition(conn, query):
    '''Returns a list of positions that match the keywords'''
    curs = dbi.dict_cursor(conn)
    LIKE_keywords = getLIKEList(query)
    sql = '''select * from jobPosition 
            where jobType %s '''
    curs.execute(sql, [LIKE_keywords])
    return curs.fetchall()

def getReferrerID(conn, query):
    '''Returns a list of referrers/one referrer 
        that matches the keywords'''
    curs = dbi.dict_cursor(conn)
    LIKE_keywords = getLIKEList(query)
    sql = '''select rid from referrer 
            where name %s '''
    curs.execute(sql, [LIKE_keywords])
    return curs.fetchall()

def searchByReferrer(conn, referrer_ids):
    '''Returns a list of referrer id that match the referrer_ids'''
    curs = dbi.dict_cursor(conn)
    referrer_id_str = ""
    for i, referrer_id in enumerated(referrer_ids):
        if i == len(keywords)-1:
            referrer_id_str = "rid = " + referrer_id
        else:
            referrer_id_str = "rid = " + referrer_id + " or "

    sql = '''select rid from referrer where %s'''
    curs.execute(sql, [referrer_id_str])
    return curs.fetchall()

def searchByCompany(conn, query):
    '''Returns a list of companies that match the keywords'''
    curs = dbi.dict_cursor(conn)
    LIKE_keywords = getLIKEList(query)
    sql = '''select * from jobPosition 
            where company %s '''
    curs.execute(sql, [LIKE_keywords])
    return curs.fetchall()

def getLIKEList (query):
    '''Returns a string in the format of LIKE '%keyword%'
    and LIKE '%keyword%' '''
    keywords = query.split()
    LIKE_keywords = ""
    for i, keyword in enumerated(keywords):
        if i == len(keywords)-1:
            LIKE_keywords += "LIKE '%" + keyword + "%'" 
        else:
            LIKE_keywords += "LIKE '%" + keyword + "%' and"
    return LIKE_keywords