from flask import Flask, jsonify, request
from random import randint
from flask_sqlalchemy import SQLAlchemy
import json
import sys
import database_handler
import re

app = Flask(__name__)
app.debug = True

def checkUserExist(email):
    data = database_handler.getUserDataByEmail(email)
    if data == None:
        return None
    return data

def persistLoggedInUsers(email, token):
    try:
        result = database_handler.add_loggedinuser(email, token)
        return result

    except Exception as e:
        print("Error:", e)
        return False
    

def persistUsers(email, password, firstname, familyname, gender, city, country, message):
    return database_handler.add_user(email, password, firstname, familyname, gender, city, country, message) 

#check the numbers of letters of the password
def validSignin(password):
    if password is None or len(password) < 7:
        return False
    return True

@app.teardown_request
def after_request(exception):
    database_handler.disconnect_db()

@app.route('/')
def welcomeview():
    return app.send_static_file("client.html")

@app.route('/sign_in', methods=['POST'])
def signin():
    data = request.get_json()
    print(data)
    email = data['username']
    password = data['password']

    #password validation
    correct = validSignin(password)
    if not correct:
        return jsonify({'success': False, 'message': "The password is at least 7 letters."})
   
    #get user data
    user_data = checkUserExist(email)
    if user_data is not None:
        #confirm the password is correct
        if user_data['password'] == password:            
            #generate a token
            letters = 'abcdefghiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
            token = ''
            for i in range(0, 36):
                token += letters[randint(0,len(letters) - 1)]
            # add loggined user data to db
            result = persistLoggedInUsers(email, token)
            if result is True:
                print(token)
                return jsonify({'success': True, 'message': "Successfully signed in.", 'data': token})
    return jsonify({'success': False, 'message': "Wrong username or password."})


def check(email):
        pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
        if email is None : return False
        if re.match(pat,email): 
            return True
        else:
            return False
               

@app.route('/sign_up', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
     
    #email validation
    isEmail = check(email)
    if isEmail is False:
        return jsonify({'success': False, 'message': "Email is not vaild."})

    # Check if all required fields are present
    required_fields = ['email', 'password', 'firstname', 'familyname', 'gender', 'city', 'country']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f"Missing or empty {field} field."})

    email = data['email']
    password = data['password']
    familyname = data['familyname']
    firstname = data['firstname']
    gender = data['gender']
    city = data['city']
    country = data['country']
    message = '[]'

    # Validate password length
    if len(password) < 7:
        return jsonify({'success': False, 'message': "Password is not at least 7 characters long."})
    
    # Check if the user already exists
    user_data = checkUserExist(email)
    if user_data is not None:
        return jsonify({'success': False, 'message': "User already exists."})

    # Persist user data in the database
    result = persistUsers(email, password, firstname, familyname, gender, city, country,message)
    if result:
        return jsonify({'success': True, 'message': "Successfully created a new user."})
    else:
        return jsonify({'success': False, 'message': "Failed to create a new user."})



@app.route('/sign_out', methods=['POST'])
def signout():
    data = request.get_json()
    token = data['token']
    
    # check this user logged in
    loggedIn = database_handler.checkTokenExist(token)
    if loggedIn:
        result = database_handler.deleteLoggedinUserByToken(token)
        return jsonify({'success': True, 'message': "Successfully signed out."})
    return jsonify({'success': False, 'message': "You are not signed in."})

@app.route('/get_user_data_by_token', methods=['GET'])
def getUserDataByToken():
    header = request.headers.get('Authorization')
    if header is None : 
        return jsonify({'success': False, 'message': "Token hedaer is not vaild"})
        

    else :
        token = request.headers['Authorization'].replace('Bearer','')
        #logged_in_user = database_handler.getloggedinUserDataByToken(token)
        loggedIn = database_handler.checkTokenExist(token)
        if loggedIn:
            email = database_handler.tokenToEmail(token)
            user_data = database_handler.getUserDataByEmail(email)
            if user_data is not None:
                user_data['token'] = token
                return jsonify({'success': True, 'message': "User data retrieved.", 'data': user_data})
            return jsonify({'success': False,'message': "No such user."})
        return jsonify({'success': False, 'message': "You are not signed in."})

@app.route('/get_user_data_by_email', methods=['GET'])
def get_user_data_by_email():
    header = request.headers.get('Authorization')
    print(header)
    data = request.get_json()
    print(data)
    email = data['email']
    token = data['token']
        
    # check this user logged in
    loggedIn = database_handler.checkTokenExist(token)
    if loggedIn:
        # get user data
        user_data = database_handler.getUserDataByEmail(email)
        if user_data is not None:
                return jsonify({'success': True, 'message': "User data retrieved.", 'data': user_data})
        return jsonify({'success': False, 'message': "No such user."})
    return jsonify({'success': False, 'message': "You are not signed in."})
            



        
@app.route('/get_user_messages_by_token', methods=['POST'])
def getUserMessagesByToken():
    data = request.get_json()
    token = data['token']
    
    # check this user logged in
    loggedIn = database_handler.checkTokenExist(token)
    if loggedIn:
        # email = database_handler.tokenToEmail(token)
        user_data = database_handler.getUserMessagesByToken(token)
        if user_data is not None:
            return jsonify({'success': True, 'message': "User messages retrieved.", 'data': user_data['messages']})
        return jsonify({'success': False,'message': "No such user."})
    else:
        return jsonify({'success': False, 'message': "You are not signed in."})
        
@app.route('/get_user_messages_by_email', methods=['POST'])
def getUserMessagesByEmail():
    data = request.get_json()
    token = data['token']
    email = data['email']
    
    # check this user logged in
    loggedIn = database_handler.checkTokenExist(token)
    if loggedIn:
        user_data = database_handler.getUserMessagesByEmail(email)
        print(user_data)
        if user_data is not None:
            return jsonify({'success': True, 'message': "User messages retrieved.", 'data': user_data['messages']})
        return jsonify({'success': False,'message': "No such user."})
    else:
        return jsonify({'success': False, 'message': "You are not signed in."})

@app.route('/post_message', methods=['POST'])
def postMessage():
    data = request.get_json()
    token = data['token']
    toEmail = data['toEmail']
    content = data['content']
    
    fromEmail = database_handler.tokenToEmail(token)
    if fromEmail is not None:
        if toEmail == "":
            toEmail = fromEmail

        # get recipient user data
        recipient = database_handler.getUserMessagesByEmail(toEmail)
        if recipient is not None:
            # add new content into recipient messages
            messages = json.loads(recipient['messages'])
            message = {'writer':fromEmail, 'content':content}
            messages.append(message)
            messages = json.dumps(messages)
            # update recipient messages data in db
            database_handler.postMessage(toEmail, messages)
            return jsonify({'success': True, 'message': "Message posted."})
        return jsonify({'success': False,'message': "No such user."})
    return jsonify({'success': False,'message': "You are not signed in."})
        

@app.route('/change_password', methods=['PUT'])
def changePassword():
    token = request.headers['Authorization'].replace('Bearer','')
    logged_in_user = database_handler.getloggedinUserDataByToken(token)
    

    if logged_in_user is not None:
        data = request.get_json()
        oldPassword = data['oldpassword']
        newPassword = data['newpassword']
        # validate the format
        if len(oldPassword) < 7 or newPassword is None :
            return jsonify({'success': False, 'message': "The password is at least 7 characters. or token is not correct."})
    
        else:
            # pass the validation
            # check the token exists
            token_exist = database_handler.checkTokenExist(token)
            if token_exist:
                email = database_handler.tokenToEmail(token)
                user_data = database_handler.getUserDataByEmail(email)
                # check the old pw is correct
                #print(email,user_data)
                if user_data['password'] == oldPassword:
                    # change password by database
                    database_handler.changePassword(email, newPassword)
                    return jsonify({'success': True, 'message': "Password changed."})
                return jsonify({ "success": False, "message": "Wrong password."})
            return jsonify({ "success": False, "message": "You are not logged in."})
    else : return jsonify({ "success": False, "message": "You are not logged in."})
        


if __name__ == '__main__':
    app.run()
