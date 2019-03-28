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


def geocode(lat,lon):

    url_template = """
    https://developers.zomato.com/api/v2.1/geocode?lat={lat}&lon={lon}&apikey={API_KEY}
    """

    url = url_template.format(lat=lat, lon=lon, API_KEY=MY_API_KEY)

    out_json = result(url)
    rest_list = [] # save as list
    for x in range(len(out_json['nearby_restaurants'])):
        sub_rest ={} # save as dictionary
        sub_rest['image'] = [ out_json['nearby_restaurants'][x]['restaurant']['thumb'] ,
                            out_json['nearby_restaurants'][x]['restaurant']['url'] ]
        sub_rest['name'] = out_json['nearby_restaurants'][x]['restaurant']['name']
        sub_rest['rating'] = out_json['nearby_restaurants'][x]['restaurant']['user_rating']["aggregate_rating"]
        sub_rest['address'] = out_json['nearby_restaurants'][x]['restaurant']['location']["address"]
        rest_list.append(sub_rest)
    return(rest_list)


def result(url):
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": MY_API_KEY}
    resp = requests.get(url, headers=header)
    if resp.ok:
        out = resp.json()
    else:
        out = resp.reason
    return(out)


""" =============================== app.route ============================== """


@app.route('/')
@app.route('/home')
def home():
    columnNames = ['path','Description']
    des = [['/nearbyres/{lat}/{lon}','key in latitude and longtitude and get nearby restaurant'],
            ['/rat/<res>/<int:rate>','Rate on this system'],
            ['/login', 'log in system'],
            ['/logout', 'log out system'],
            ['/newuser', 'create new account']]
    return render_template('home.html', colnames=columnNames, des=des)


@app.route('/nearbyres/<lat>/<lon>', methods=["GET"])
@login_required
def render_dashboard(lat,lon):
    url_root = request.url_root
    temp = geocode(lat,lon)
    columnNames = ['','name','rating','address']
    return render_template('result.html', url_root=url_root,records=temp, colnames=columnNames), 201


@app.route('/rat/<res>/<rate>', methods=["GET"])
@login_required
def rate_restaurant(res,rate):
    if not rate.isdigit():
        return '<h2>rating: must be an integer!</h2>', 201
    elif int(rate)>5 or int(rate)<0 :
        return '<h2>rating: only intergers between 0~5 are available!</h2>', 201
    else:
        insert_cql = """INSERT INTO irene.restaurant_rating (username, res_name, created_time, rating) VALUES
                     ('{}','{}', toUnixTimestamp(now()),{});""".format(current_user.id,res,rate)
        session.execute(insert_cql)
        return '<h2>Tanks for your feedback</h2>', 201


# just for reviewing
@app.route('/rat/db', methods=["GET"])
@login_required
def restaurant_rating_db():
    rows = session.execute("SELECT * FROM irene.users ORDER BY time DESC;")
    return jsonify(list(rows))
