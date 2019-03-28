"""
This file mainly used for implementing user accounts and access management and hash-based authentication
It uses flask_login package to remember users and uses Cassandra to save user info.
reference: https://github.com/maxcountryman/flask-login
"""
from flask import Flask, url_for, request, redirect, jsonify, json
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from cassandra.cluster import Cluster
from flask import Blueprint
from passlib.apps import custom_app_context as pwd_context
from app import app


auth_api = Flask(__name__)
# user blueprint functin to call another file
auth_api.register_blueprint(app)
auth_api.secret_key = 'IRENE_SECRET_KEY'
login_manager = LoginManager(auth_api)

cluster = Cluster()
session = cluster.connect()

template_page = """
             <form action={} method='POST'>
             <input type='text' name='email' id='email' placeholder='email'/>
             <input type='password' name='password' id='password' placeholder='password'/>
             <input type='submit' name='submit'/>
             </form>
             """

#if want to add more judgement, modify from here
class User(UserMixin):
    pass


# When user sign up, this function will be called
class Create:
    # save username and hashed password into database
    def new_user(self, name, password):
        password = self.hash_password(password)
        insert_cql = """INSERT INTO irene.users (username, password_hash, time) VALUES
                    ('{}','{}', toUnixTimestamp(now()));""".format(name,password)
        session.execute(insert_cql)

    # trigger this function when a new user registers or a user changes the password
    # convert original password to  a hashed one and store it
    def hash_password(self, password):
        password_hash = pwd_context.encrypt(password)
        return password_hash

# flask_login save current user id
@login_manager.user_loader
def user_loader(email):
    user = User()
    user.id = email
    return user


# log in page
@auth_api.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_active:
        return "<h2>Already Login</h2>" + \
                "<a href='{}home'>Home</a>".format(request.url_root), 201

    # a page to enter username and password
    if request.method == 'GET':
        log_in_page = "<h2>Log-in</h2>" + template_page.format('login') + \
                    "<a href='{}newuser'>Sign Up</a>".format(request.url_root)
        return log_in_page

    log_in_page = "<h2>Log-in</h2>" + template_page.format('login') + \
                "<a href='{}newuser'>Sign Up</a>".format(request.url_root)

    email = request.form['email']
    ori_password = request.form['password']
    rows = session.execute("SELECT password_hash FROM irene.users where username = %s LIMIT 1", ([email]))
    if not rows: # fool-proofing: username not exists
        return ('<h2>Username:{} does not exist</h2>{}'.format(email,log_in_page)), 404
    elif pwd_context.verify(ori_password, rows[0].password_hash)==False:
        # fool-proofing: wrong password
        return ('<h2>Wrong password. Please Log in again</h2>{}'.format(log_in_page)), 404
    else:
        user = User()
        user.id = email # id as email
        login_user(user) # remember user_id
        return ("""<h2>Log in success. Hello, {}
                </h2><a href='{}home'>Home</a>""".format(current_user.id, request.url_root)), 201

    if request.method == 'POST': # create new user
        email = request.json['email'] # Your form's
        ori_password = request.json['email'] # input names
        Create().new_user(email, ori_password)
        login_user(email)
        return ('<h1>Hello, {}.</h1>'.format(email)) ,201 # Success
    return 'Bad login',404


# log out and remove log-in status
@auth_api.route('/logout')
def logout():
    logout_user()
    return 'Logged out'


# Add new user name and password to Cassandra DB
@auth_api.route('/newuser', methods=['GET', 'POST'])
def new_user():
    # Polish Sign up page
    sign_up_page = "<h2>Sign-up</h2>" + template_page.format('newuser') + \
                    "<a href='{}login'>Log in</a>".format(request.url_root)
    if request.method == 'GET':
        return sign_up_page

    email = request.form['email']
    ori_password = request.form['password']
    # fool-proofing: username already exists
    rows = session.execute("SELECT * FROM irene.users where username = %s ", ([email]))
    if rows:
        return ('<h1>username: {} already exists</h1>'.format(email)), 404
    # call function in class: save username and hashed password into database
    Create().new_user(email, ori_password)
    user = User()
    user.id = email # id as email
    login_user(user)
    return ("""<h2>Hello, {}</h2>
            <a href='{}home'>Home</a>""".format(current_user.id, request.url_root)), 201


if __name__ == '__main__':
    auth_api.run(port=8080, debug=True,use_reloader=True, use_debugger=True)
