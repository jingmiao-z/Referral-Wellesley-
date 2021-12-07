
import cs304dbi as dbi

def retrieve_announcement(conn):
    ''' Retrieve all announcements from the database'''
    curs = dbi.dict_cursor(conn)
    sql = 'select announceid, announcement from announce' 
    curs.execute(sql)
    return curs.fetchall()