
import cs304dbi as dbi

def searchByPosition(conn, query):
    '''Returns a list of positions that match the position keywords'''
    curs = dbi.dict_cursor(conn)
    list_of_keywords = percentageKeyword(query.split())
    sql = getSQL(len(list_of_keywords), "positionName")
    curs.execute(sql, list_of_keywords)
    return curs.fetchall()

def percentageKeyword(list_of_keywords):
    ''' Generate list of keywords with % sign
    ie. if the list_of_keywords is ['a', 'b'], the result is 
    ['%a%', '%b%'] '''
    for i in range(len(list_of_keywords)):
        list_of_keywords[i] = '%' + list_of_keywords[i] + '%'
    return list_of_keywords

def searchByReferrer(conn, query):
    '''Returns a list of positions that match the referrer keywords'''
    curs = dbi.dict_cursor(conn)
    list_of_keywords = percentageKeyword(query.split())
    sql = getSQL(len(list_of_keywords), "referrerName")
    curs.execute(sql, list_of_keywords)
    return curs.fetchall()

def searchByCompany(conn, query):
    '''Returns a list of positions that match the company keywords'''
    curs = dbi.dict_cursor(conn)
    list_of_keywords = percentageKeyword(query.split())
    sql = getSQL(len(list_of_keywords), "company")
    curs.execute(sql, list_of_keywords)
    return curs.fetchall()

def getSQL (length, search_by):
    '''Generate sql string in order to query from jobPosition
    when the input is a list of values.
    ie. if search_by is 'company' and the length is 2, 
    the final returned sql is
    'select * form jobPosition where (company LIKE %s and company LIKE %s)'''
    sql = 'select * from jobPosition where '
    sql += (search_by + ' LIKE %s and ') * (length-1)
    sql += search_by + ' LIKE %s'
    return sql

def get_matched_position_names(conn, keyword):
    ''' Get the name of the positions as a list of 
        dictionaries that contains the given keyword. 
        ie. given keyword is "sof". This method will 
        select all the distinct position names that contain
        'sof'.'''
    curs = dbi.dict_cursor(conn)
    sql = '''select distinct trim(positionName) as positionName
        from jobPosition where positionName LIKE %s'''
    curs.execute(sql, ['%' + keyword + '%'])    
    return curs.fetchall()

def get_matched_company_names(conn, keyword):
    ''' Get the name of the companies as a list of 
        dictionaries that contains the given keyword. 
        ie. given keyword is "mic". This method will 
        select all the distinct company names that contain
        'mic'.'''
    curs = dbi.dict_cursor(conn)
    sql = '''select distinct trim(company) as company
        from jobPosition where company LIKE %s'''
    curs.execute(sql, ['%' + keyword + '%'])    
    return curs.fetchall()

def get_matched_referrer_names(conn, keyword):
    ''' Get the name of referrers as a list of 
        dictionaries that contains the given keyword. 
        ie. given keyword is "sar". This method will 
        select all the distinct referrers names that contain
        'sar'.'''
    curs = dbi.dict_cursor(conn)
    sql = '''select distinct trim(referrerName) as referrerName
        from jobPosition where referrerName LIKE %s'''
    curs.execute(sql, ['%' + keyword + '%'])    
    return curs.fetchall()
