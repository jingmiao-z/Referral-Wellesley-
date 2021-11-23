
import cs304dbi as dbi

def retrieve_student_profile(conn, uid):
    ''' Retrieve student profile using uid '''
    curs = dbi.dict_cursor(conn)
    sql = ''' select major, minor, file, preferredLocation, description 
                from student where sid = %s '''
    curs.execute(sql,[uid])
    return curs.fetchone()

def retrieve_referrer_profile(conn, uid):
    ''' Retrieve referrer profile using uid '''
    curs = dbi.dict_cursor(conn)
    sql = ''' select company, position, emailPrefer, otherContact, linkedin, phoneNumber
                from referrer where rid = %s '''
    curs.execute(sql,[uid])
    return curs.fetchone()

def update_student_profile(conn,sid,major,minor,file,loc,des):
    ''' Update student profile using sid '''
    curs = dbi.dict_cursor(conn)
    sql = ''' update student set 
            major=%s, minor=%s, file=%s, preferredLocation=%s, description=%s 
            where sid=%s '''
    curs.execute(sql,[major,minor,file,loc,des,sid])
    conn.commit()

def update_referrer_profile(conn,rid,company,position,emailPrefer,otherContact,linkedin,phoneNumber):
    ''' Update Referrer profile using rid '''
    curs = dbi.dict_cursor(conn)
    sql = ''' update referrer set 
            company=%s, position=%s, emailPrefer=%s, otherContact=%s, 
            linkedin=%s, phoneNumber=%s
            where rid=%s'''
    curs.execute(sql,[company,position,emailPrefer,otherContact,linkedin,phoneNumber,rid])
    conn.commit()