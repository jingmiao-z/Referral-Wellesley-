
import cs304dbi as dbi

def name(conn,uid):
    '''Return name of user according to uid
    we guarantee that uid exist in table '''
    curs = dbi.dict_cursor(conn)
    sql = 'select name from user where uid = %s'
    curs.execute(sql,[uid])
    return curs.fetchone()['name']

def storeJob(conn,rid,company,pos_name,referrer_name,postionLocation,
            materialNeeded,submitDeadline):
    '''Store the Job in jobPosition table'''
    try: 
        curs = dbi.dict_cursor(conn)
        sql = '''INSERT INTO jobPosition (rid, company, positionName, 
        referrerName,postionLocation,materialNeeded,submitDeadline) VALUES 
        (%s,%s,%s,%s,%s,%s,%s)'''
        curs.execute(sql,[rid,company,pos_name,referrer_name,postionLocation,
            materialNeeded,submitDeadline])
        conn.commit()
    except Exception as err:
        print('something went wrong', repr(err))
    
def retrieve_position(conn, pid):
    ''' Retrieve one position detail using the given pid '''
    curs = dbi.dict_cursor(conn)
    sql = 'select * from jobPosition where pid = %s'
    curs.execute(sql,[pid])
    return curs.fetchone()

def retrieve_referrer_contact(conn, rid):
    ''' Retrieve referrer contact information using the given rid '''
    curs = dbi.dict_cursor(conn)
    sql = '''select emailPrefer, phoneNumber, linkedin, otherContact 
        from referrer where rid = %s'''
    curs.execute(sql,[rid])
    return curs.fetchone()

def retrieve_pid(conn, sid):
    ''' retrieve position id according to the sid given '''
    curs = dbi.dict_cursor(conn)
    sql = 'select pid from refer where sid = %s'
    curs.execute(sql,[sid])
    return curs.fetchall()

def retrieve_applied_positions(conn, sid):
    ''' Retrieve list of position details that this 
        current student applied'''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from jobPosition inner join refer
            using (pid)
            where sid = %s'''
    curs.execute(sql, [sid])
    return curs.fetchall()

def retrieve_applied_student(conn, rid):
    ''' Retrieve list of students and their info who applied 
        to the positions posted by this specific referrer'''
    curs = dbi.dict_cursor(conn)
    sql = '''select refer.pid, sid, positionName, referStatus, name as studentName 
            from jobPosition inner join refer using(pid) 
            inner join student using(sid)
            where refer.rid = %s'''
    curs.execute(sql, [rid])
    return curs.fetchall()

def student_detail(conn,sid):
    ''' Retrieve Why Position and Why Company and student information given sid'''
    curs = dbi.dict_cursor(conn)
    sql = '''select name, major, minor, file, description,
            whyCompany, whyPosition
            from refer inner join student using (sid) 
            where sid = %s;'''
    curs.execute(sql, [sid])
    return curs.fetchone()

def change_status(conn,status,rid,sid,pid):
    '''change the refer status of in refer table according to what
    the referrer submitted in the form '''
    # the method is not working properly 
    curs = dbi.dict_cursor(conn)
    sql = '''update refer set referStatus = %s where rid = %s and sid = %s and pid = %s'''
    # update refer set referStatus = "waiting" where rid = 2 and sid = 1 and pid = 1;
    curs.execute(sql,[status,rid,sid,pid])
    conn.commit()