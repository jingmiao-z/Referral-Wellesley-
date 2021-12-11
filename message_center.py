
import cs304dbi as dbi

def student_notification(conn,status,rid,sid,pid):
    '''store the notification in announcement in student with sid given when referrers change status'''
    try:
        curs = dbi.dict_cursor(conn)
        sql = 'select referrerName, positionName from jobPosition where pid = %s'
        curs.execute(sql,[pid])
        dic = curs.fetchone() 
        announcement = "Referrer " + dic["referrerName"] + " " 
        + status + " your referral application for position " 
        + dic["positionName"]
        #see app.py 424
        sql = '''INSERT INTO announce (announcement, type, announcement_target) 
                VALUES (%s,"Student",%s)'''
        curs.execute(sql,[announcement,"Student",sid])
        curs.commit()
    except Exception as err:
        print('something went wrong', repr(err))

def referrer_notification(conn,rid,pid,sid):
    '''store the notification for referrer with given 
    rid when student ask for referral for their posted job position'''
    try:        
        curs = dbi.dict_cursor(conn)
        sql = 'select positionName from jobPosition where pid = %s'
        curs.execute(sql,[pid])
        dic = curs.fetchone() 
        positionName = dic["positionName"]
        #381
        sql = '''select name from student where sid = %s'''
        curs.execute(sql,[sid])
        dic = curs.fetchone() 
        studentName = dic["name"]
        announcement = "Student " + studentName + 
        " has applied for referral for position " + positionName
        sql = '''INSERT INTO announce (announcement, type, announcement_target) 
                VALUES (%s,"Referrer",%s)'''
        curs.execute(sql,[announcement,rid])
        conn.commit()
    except Exception as err:
        print('something went wrong', repr(err))
 
#change this later
def retrieve_announcement(conn,uid,account_type):
    ''' Retrieve all announcements from the database 
    that is revelant to user with given uid
    We will only retrieve 5 most recent ones '''
    curs = dbi.dict_cursor(conn)
    sql = '''select announcement from announce
            where (type = %s and announcement_target = %s) or type = 'All'
            order by announceid desc limit 5'''
    print(sql)
    curs.execute(sql,[account_type,uid])
    return curs.fetchall()

def admin_make_announce(conn, aid, announcement):
    ''' Get the announcement that admin just submitted 
        and store it in the database '''
    curs = dbi.dict_cursor(conn)
    sql = '''INSERT INTO announce (aid, announcement, type) 
            VALUES (%s, %s, %s)'''
    curs.execute(sql,[aid, announcement, "All"])
    conn.commit()

def retrieve_announcement_by_admin(conn, aid):
    ''' Retrieve all announcements that are sent by this admin
        from the database'''
    curs = dbi.dict_cursor(conn)
    sql = '''select announceid, announcement 
            from announce where aid = %s '''
    curs.execute(sql, [aid])
    return curs.fetchall()