from flask import redirect, request, jsonify, make_response
from application import app, cur
from application.model import Cafeteria, fetch_cafeteria, update_cafeteria
from functools import wraps
import requests, json, jwt, datetime
import hashlib

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        id = int(request.args.get('id'))
        if not token:
            return make_response('Token is missing!', 403)
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],"HS256")
            cafeteria = fetch_cafeteria({'id':id})[0]
        except:
            return make_response('Token is invalid', 403)
        return f(cafeteria, *args, **kwargs)
    return decorated

@app.route('/verify')
@token_required
def verify(cafeteria):
    return make_response("Token is valid", 200)

@app.route('/location')
def location():
    cafeterias = fetch_cafeteria()
    return_list = []
    for cafeteria in cafeterias:
        return_list.append(cafeteria.getAttr())
    return make_response(jsonify(return_list))

@app.route('/login',methods=['POST'])
def login():
    data = request.json
    id = data['id']
    password = data['password']
    cafeteria = fetch_cafeteria({'id':id})[0]
    userInput = hashlib.md5(str.encode(password+cafeteria.salt)).hexdigest()
    if cafeteria and cafeteria.password == userInput:
        token = jwt.encode({'id': cafeteria.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'],algorithm='HS256')
        return make_response(jsonify(
            {
                'token' : token,
                'message' : "Login successfully."
            }
        ), 200)
    return make_response(jsonify(
            {
                'message' : "Login Failed."
            }
        ), 403)
    

@app.route('/update', methods=["PUT"])
@token_required
def update(cafeteria:Cafeteria):
    try:
        updated_info = json.loads(request.json)
        update_cafeteria(updated_info, {'id':cafeteria.id})
    except:
        return make_response(jsonify({'message': "Update failed."}), 403)
    return make_response(jsonify({'message': "Update successfully."}), 201)

