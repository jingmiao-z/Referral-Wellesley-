
import cs304dbi as dbi

def getPassword(conn, email):
    '''Returns the password and user_type as tuple'''
    curs = dbi.dict_cursor(conn)
    sql = '''select password, type
            from movie 
            where email ='''
    curs.execute(sql, [email])
    dict = curs.fetchone()
    if len(dict) == 0:
        return (None,None)
    return (dict[0]["password"],dict[0]["type"])

