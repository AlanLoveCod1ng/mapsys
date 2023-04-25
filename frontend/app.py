from flask import Flask, jsonify, request, flash, url_for
from flask import render_template, redirect, make_response
import requests
import json
from model import Cafeteria
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba250'

centerIndex = -1

proxy = "http://127.0.0.1:8080"

cafeteria_id = None

def create_object():
    try:
        response = requests.get(proxy+"/location").text
    except:
        response = "[]"
    dict_list = json.loads(response)
    cafeterias = []
    for c_dict in dict_list:
        cafeterias.append(Cafeteria(c_dict))
    return cafeterias



@app.route("/")
def index():
    return redirect("/map") 

@app.route("/map", methods=['GET', 'POST'])
def map():
    global centerIndex
    centerIndex = int(request.args.get("highlight","-1"))
    response = make_response(render_template("map.html"))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response





@app.route("/dashboard",methods=['GET','POST'])
def table():
    cafeterias = create_object()
    cafes = []
    dinings = []
    fasts = []
    for c in cafeterias:
        if c.type == "Cafe":
            cafes.append(c)
        elif c.type == "Dining":
            dinings.append(c)
        elif c.type == "Fast Food":
            fasts.append(c)
    type_dict = {
        "Fast food" : fasts,
        "Cafe" : cafes,
        "Dining hall":dinings
    }
    return make_response(render_template("dashboard.html", type_dict = type_dict))



@app.route("/home")
def home():
    token = request.cookies.get('sessionID','')
    global cafeteria_id
    response = requests.get(url=proxy+"/verify?token="+token+"&id="+str(cafeteria_id))
    if response.status_code != 200:
        token = ""
        cafeteria_id = None
        return make_response(render_template('denied.html'))
    cafeterias = create_object()
    selected_cafe = None
    for cafeteria in cafeterias:
        if int(cafeteria.id) == int(cafeteria_id):
            selected_cafe = cafeteria
    if not selected_cafe:
        return make_response("Invalid cafeteria id.", 403)
    return make_response(render_template("worker.html", cafeteria=selected_cafe, proxy=proxy))

@app.route("/location/<cafe_id>",methods=['GET'])
def update(cafe_id):
    cafeterias = create_object()
    token = request.cookies.get('sessionID', '')
    changed_cafe = None
    for cafeteria in cafeterias:
        if cafeteria.id == int(cafe_id):
            changed_cafe = cafeteria
    if not changed_cafe:
        return make_response("Invalid cafeteria id.", 403)
    wait_dict = {
        "lt5min" : "< 5 min",
        "5-15min"  : "5 - 15 min",
        "gt20min" : "> 20 min",
        "< 5 min" : "< 5 min",
        "5 - 15 min" : "5 - 15 min",
        "> 20 min" : "> 20 min"
    }
    changed_cafe.status = request.args.get("status", changed_cafe.status)

    changed_cafe.wait_times = wait_dict[request.args.get("wait_times", changed_cafe.wait_times)]
    to_update = json.dumps(changed_cafe.getAttr())
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
    url = proxy+"/update?id="+cafe_id+"&token="+token
    response = requests.put(url=url,headers=headers,json=to_update)
    return "Done"


@app.route("/highlight", methods = ['GET','POST'])
def highlight():
    global centerIndex
    response = json.dumps([centerIndex])
    centerIndex = -1
    return response





@app.route('/login',methods = ['POST'])  
def login():
    global cafeteria_id  
    body = request.form  
    url = proxy+ "/login"  
    headers = {
        'Accept': 'application/json',  
        'Content-Type': 'application/json'
        }
    response = requests.post(url=url, headers=headers, json=body)  
    if response.status_code != 200: 
        return redirect(url_for(".workerlogin", messages = json.dumps({"main":"Login failed on page baz"}))) 
    token = response.json()['token']
    cafeteria_id = body['id']
    print(cafeteria_id)
    resp = redirect(f"/home")
    resp.set_cookie('sessionID',token)
    return resp

@app.route('/logout')
def logout():
    resp = redirect("/workerlogin")
    resp.delete_cookie('sessionID')
    return resp


@app.route("/locations", methods = ['GET','POST'])
def locations():
    cafeterias = create_object()
    dict_list = []
    for c in cafeterias:
        dict_list.append(c.getAttr())
    return jsonify(dict_list)

@app.route("/workerlogin",methods=['GET','POST'])
def workerlogin():
    token = request.cookies.get('sessionID','')
    if token != "":
        return redirect("/home")
    print(token)
    cafeteria = create_object()
    if 'messages' in request.args:
        return make_response(render_template("login.html", cafeterias = cafeteria, failed = True))
    return make_response(render_template("login.html", cafeterias = cafeteria, failed = False))

@app.route("/JoininPage",methods=['GET','POST'])
def Join():
    cafeteria = create_object()
    return make_response(render_template("joinin.html", cafeterias = cafeteria, failed = False))

@app.route("/Test",methods=['GET','POST'])
def Test():
    cafeteria = create_object()
    return make_response(render_template("test.html"))



@app.route("/user")
def user():
    cafeteria = create_object()
    return make_response(render_template("user.html", cafeterias = cafeteria))


if __name__ == '__main__':
    app.run(debug=True)