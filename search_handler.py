
import cs304dbi as dbi

def searchByPosition(conn, query):
    '''Returns a list of positions that match the keywords'''
    
    curs = dbi.dict_cursor(conn)
    list_of_keywords = percentageKeyword(query.split())
    sql = getSQL(len(list_of_keywords), "positionName")
    curs.execute(sql, list_of_keywords)
    return curs.fetchall()

def percentageKeyword(list_of_keywords):
    for i in range(len(list_of_keywords)):
        list_of_keywords[i] = '%' + list_of_keywords[i] + '%'
    return list_of_keywords

# def getReferrerID(conn, query):
#     '''Returns a list of referrers/one referrer 
#         that matches the keywords'''
#     curs = dbi.dict_cursor(conn)
#     LIKE_keywords = getLIKEList(query, "name")
#     sql = '''select rid, name from referrer 
#             where name %s '''
#     curs.execute(sql, [LIKE_keywords])
#     return curs.fetchall()

def searchByReferrer(conn, query):
    '''Returns a list of referrer id that match the referrer names'''
    curs = dbi.dict_cursor(conn)
    LIKE_keywords = getLIKEList(query, "jobPosition")
    sql = '''select * from jobPosition where name %s'''
    print(sql)
    curs.execute(sql, [LIKE_keywords])
    return curs.fetchall()

def searchByCompany(conn, query):
    '''Returns a list of companies that match the keywords'''
    curs = dbi.dict_cursor(conn)
    LIKE_keywords = getLIKEList(query, "company")
    sql = '''select * from jobPosition 
            where company %s '''
    curs.execute(sql, [LIKE_keywords])
    return curs.fetchall()

def getSQL (length, search_by):
    ''' '''
    sql = 'select * from jobPosition where '
    sql += (search_by + ' LIKE %s and ') * (length-1)
    sql += search_by + ' LIKE %s'
    print(sql)
    return sql

# def getRIDList (referrer_ids):
#     '''Returns a string in the format of 
#     'rid = keyrid or rid = keyrid' '''
#     referrer_id_str = ""
#     for i, referrer_id in enumerated(referrer_ids):
#         if i == len(keywords) - 1:
#             referrer_id_str = "rid = " + referrer_id
#         else:
#             referrer_id_str = "rid = " + referrer_id + " or "
#     return referrer_id_str