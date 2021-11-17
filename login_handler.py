
import cs304dbi as dbi

def getPassword(conn, email):
    '''Returns the password and user_type as tuple'''
    curs = dbi.dict_cursor(conn)
    sql = '''select password, type
            from user 
            where email = %s'''
    curs.execute(sql, [email])
    result = curs.fetchone()
    if not result:
        return ("","")
    return (result['password'], result['type'])

