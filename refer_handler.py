
import cs304dbi as dbi

def ask_for_refer(conn,rid, sid, pid, whyCompany, whyPosition):
    ''' Insert the information into refer database '''
    curs = dbi.dict_cursor(conn)
    sql = '''INSERT INTO refer 
    (rid, sid, pid, whyCompany,whyPosition, referStatus) 
    VALUES (%s,%s,%s,%s,%s, "waiting")'''
    curs.execute(sql,[rid,sid,pid,whyCompany,whyPosition])
    conn.commit()
    
def check_duplicate_request(conn, rid, sid, pid):
    ''' Return true if the student already asked for a referral of specific postion. 
        Otherwise, return false '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from refer where rid = %s and sid = %s and pid = %s '''
    curs.execute(sql,[rid,sid,pid])
    return curs.fetchone() != None