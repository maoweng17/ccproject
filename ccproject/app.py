"""
This page mainly used for accessing external API data and Cassandra DB
"""
import flask
from flask import Flask, Response, redirect, request, session, abort,render_template,Blueprint,jsonify
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
import requests
from cassandra.cluster import Cluster

app = Blueprint('app', __name__)
cluster = Cluster()
session = cluster.connect()

""" =============================== Function ============================== """
MY_API_KEY = '65813367be3b71f890112a4f702d8536'

# retrieve data from external API and save as dictionary format
def geocode(lat,lon):

    # external API user_template ( allow user to enter latitude and longtitude)
    url_template = """
    https://developers.zomato.com/api/v2.1/geocode?lat={lat}&lon={lon}&apikey={API_KEY}
    """

    url = url_template.format(lat=lat, lon=lon, API_KEY=MY_API_KEY)

    out_json = result(url)
    rest_list = [] # initilise list
    for x in range(len(out_json['nearby_restaurants'])):
        sub_rest ={} # retrieve each information and save as dictionary
        sub_rest['image'] = [ out_json['nearby_restaurants'][x]['restaurant']['thumb'] ,
                            out_json['nearby_restaurants'][x]['restaurant']['url'] ]
        sub_rest['name'] = out_json['nearby_restaurants'][x]['restaurant']['name']
        sub_rest['rating'] = out_json['nearby_restaurants'][x]['restaurant']['user_rating']["aggregate_rating"]
        sub_rest['address'] = out_json['nearby_restaurants'][x]['restaurant']['location']["address"]
        rest_list.append(sub_rest)
    return(rest_list)

# after accessing API, check whether reponse correctly
def result(url):
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": MY_API_KEY}
    resp = requests.get(url, headers=header)
    if resp.ok:
        out = resp.json()
    else:
        out = resp.reason
    return(out)


""" =============================== app.route ============================== """

# Home page: list each page and description
@app.route('/')
@app.route('/home')
def home():
    columnNames = ['path','Description','require log-in?']
    des = [['/nearbyres/{float:lat}/{float:lon}','key in latitude and longtitude and get nearby restaurant','Yes'],
            ['/rat/{res}/{int:rate}','Rate on this system','Yes'],
            ['/login', 'log in system','No'],
            ['/logout', 'log out system','No'],
            ['/newuser', 'create new account','No'],
            ['/rat/db', 'Show rating information','Yes'],
            ['/user/db', 'Show user information','Yes']]
    return render_template('home.html', colnames=columnNames, des=des)


# Get Nearby restaurant by entering latitude and longtitude
@app.route('/nearbyres/<float:lat>/<float:lon>', methods=["GET"])
@login_required
def render_dashboard(lat,lon):
    url_root = request.url_root
    temp = geocode(lat,lon) # trigger function to get dictionary
    columnNames = ['','name','rating','address'] # Static Column Names
    return render_template('nearby.html', url_root=url_root,records=temp, colnames=columnNames), 200


# fake POST function, insert information to database
# user can give rating for restaurant
@app.route('/rat/<res>/<rate>', methods=["GET"])
@login_required
def rate_restaurant(res,rate):
    # fool-proofing: rating is not an integer
    if not rate.isdigit():
        return '<h2>rating: must be an integer!</h2>', 400
    # fool-proofing: rating value out of bound
    elif int(rate)>5 or int(rate)<0 :
        return '<h2>rating: only intergers between 0~5 are available!</h2>', 400
    else:
        # sucess: insert data into database
        insert_cql = """INSERT INTO irene.restaurant_rating (username, res_name, created_time, rating) VALUES
                     ('{}','{}', toUnixTimestamp(now()),{});""".format(current_user.id,res,rate)
        session.execute(insert_cql)
        # return '<title>Give rating Successfully</title><h2>Tanks for your feedback</h2>', 201
        return render_template('result.html', title='Give rating Successfully',
                                h2='Tanks for your feedback',root=request.url_root), 201

# retrieve data from Cassandra DB to check whether rating info. be stored
# just for reviewing ( for demo convenience)
@app.route('/rat/db', methods=["GET"])
@login_required
def restaurant_rating_db():
    rows = session.execute("SELECT * FROM irene.restaurant_rating ;")
    return jsonify(list(rows))


# retrieve data from Cassandra DB to check whether user info. be stored
# just for reviewing ( for demo convenience)
@app.route('/user/db', methods=["GET"])
@login_required
def user_db():
    rows = session.execute("SELECT * FROM irene.users ;")
    return jsonify(list(rows))
