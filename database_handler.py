#database handler
import sqlite3
from flask import g

DATABASE_URI = "database.db"

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
    return db

def disconnect_db():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()
        g.db = None

def add_user(email, password, firstname, familyname, gender, city, country, message):
    get_db().execute('insert into users values (?, ?, ?, ?, ?, ?, ?, ?)', [email, password, familyname, firstname, gender, city, country, message])
    get_db().commit()
    return True

def add_loggedinuser(email, token):
    print(email)
    get_db().execute('insert into loggedinusers values (?, ?)',[email, token])
    get_db().commit()
    return True

def checkTokenExist(token):
    cursor = get_db().execute('select * from loggedinusers where token = ?', [token])
    row = cursor.fetchone()
    if row is not None:
        cursor.close()
        return True
    return False

def deleteLoggedinUserByToken(token):
    cursor = get_db().execute('select * from loggedinusers where token = ?', [token])
    get_db().execute('delete from loggedinusers where token = ?', [token])
    get_db().commit()
    cursor.close()

def tokenToEmail(token):
    if token != "":
        cursor = get_db().execute('select * from loggedinusers where token = ?', [token])
        rows = cursor.fetchall()
        #print("rows:",rows)
        if rows:
            email = rows[0][0]
            return email
        else : return False
    



def getloggedinUserDataByToken(token):
    #get email by token
    email = tokenToEmail(token)
    return getloggedUserDataByEmail(email)

def getloggedUserDataByEmail(email):
    cursor = get_db().execute('select * from loggedinusers where email = ?', [email])
    rows = cursor.fetchone()
    cursor.close()
    if rows is not None:
        result = {
            'email': rows[0],
            'token': rows[1],
        }
        return result
    return None

def getUserDataByToken(token):
    #get email by token
    email = tokenToEmail(token)
    return getUserDataByEmail(email)

def getUserDataByEmail(email):
    cursor = get_db().execute('select * from users where email = ?', [email])
    rows = cursor.fetchone()
    cursor.close()
    if rows is not None:
        result = {
            'email': rows[0],
            'password': rows[1],
            'familyname': rows[2],
            'fitstname': rows[3],
            'gender': rows[4],
            'city': rows[5],
            'country': rows[6],
        }
        return result
    return None

def getUserMessagesByToken(token):
    email = tokenToEmail(token)
    return getUserMessagesByEmail(email)    

def getUserMessagesByEmail(email):
    cursor = get_db().execute('select * from users where email = ?', [email])
    rows = cursor.fetchone()
    cursor.close()
    # print(rows)
    if rows is not None:
        result = {
            'messages': rows[7]
        }
        return result
    return None

def changePassword(email, new_password):
    cursor = get_db().execute('UPDATE users SET password = ? WHERE email = ?', [new_password, email])
    get_db().commit()
    cursor.close()
    return True

def postMessage(email, messages):
    print(messages)
    cursor = get_db().execute('update users SET messages = ? where email = ?', [messages, email])
    get_db().commit()
    cursor.close()
    return True
