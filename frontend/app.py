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
        return redirect('/logout')
    cafeterias = create_object()
    selected_cafe = None
    for cafeteria in cafeterias:
        if int(cafeteria.id) == int(cafeteria_id):
            selected_cafe = cafeteria
    if not selected_cafe:
        return make_response("Invalid cafeteria id.", 403)
    resp_code = 0
    if 'messages' in request.args:
        resp_code = json.loads(request.args['messages'])['response']
    return make_response(render_template("worker.html", cafeteria=selected_cafe,resp_code = resp_code))

@app.route("/location/<cafe_id>",methods=['POST'])
def update(cafe_id):
    cafeterias = create_object()
    form = request.form
    print(form)
    token = request.cookies.get('sessionID', '')
    changed_cafe = None
    for cafeteria in cafeterias:
        if cafeteria.id == int(cafe_id):
            changed_cafe = cafeteria
    if not changed_cafe:
        return make_response("Invalid cafeteria id.", 403)

    changed_cafe.status = form.get("status", changed_cafe.status)

    changed_cafe.wait_times = form.get("wait-times", changed_cafe.wait_times)
    to_update = json.dumps(changed_cafe.getAttr())
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
    url = proxy+"/update?id="+cafe_id+"&token="+token
    response = requests.put(url=url,headers=headers,json=to_update)
    if response.status_code == 201:
        return redirect(url_for('.home', messages=json.dumps({"response":1})))
    return redirect(url_for('.home', messages=json.dumps({"response":2})))


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
    if token != "" and cafeteria_id != None:
        return redirect("/home")
    cafeteria = create_object()
    if 'messages' in request.args:
        return make_response(render_template("login.html", cafeterias = cafeteria, failed = True))
    return make_response(render_template("login.html", cafeterias = cafeteria, failed = False))

if __name__ == '__main__':
    app.run(debug=True)