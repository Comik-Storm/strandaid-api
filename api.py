import os
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, render_template, Response, request
import json

#Setup Google Firebase
cred = credentials.Certificate('/home/ComikStorm/mysite/key.json')
firebase = initialize_app(cred)

#Setup Firestore DB
db = firestore.client()
records = db.collection('records')
drones = db.collection('captures')

app = Flask(__name__)
app.config['upload'] = '/home/ComikStorm/mysite/images'


@app.route('/', methods=['GET'])
def home():
    return "Hello From Team Strandaid!"


@app.route('/objects', methods=['POST'])
def objects():
    try:
        if 'file' not in request.files:
            return "FileNot Found!"
        file = request.files['file']
        file.save(os.path.join(app.config['upload'], file.filename))
        data = json.loads(request.form.get('data'))
        newData = {
                "imageBy": data["imageBy"],
                "imgUrl": file.filename,
                "lat": data["lat"],
                "long": data["long"],
                "object": data["object"],
                "time": data["time"]
                 }
        drones.add(newData)
        return jsonify({"success": True}), 200
    except Exception as e:
        return e



@app.route('/drone_record', methods=['GET'])
def droneList():
    try:
        docs = drones.stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())
        return jsonify(data), 200
    except Exception as e:
        return "An Error Occurred"


@app.route('/all', methods=['GET'])
def all():
    try:
        docs = records.stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())
        return jsonify(data), 200
    except Exception as e:
        return e



@app.route('/list', methods=['GET'])
def list():
    try:
        record_id = request.args.get('id')
        docs = records.stream()
        for doc in docs:
            data = doc.to_dict()
            if data["drone_id"] == int(record_id):
                return jsonify(data), 200
        return "No Data Found!"
    except Exception as e:
        print(e)
        return "An Error Occurred"


@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        records.add(data)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return "An Error Occurred"


@app.route('/clear', methods=['GET', 'DELETE'])
def clear():
    try:
        docs = records.stream()
        for doc in docs:
            doc.reference.delete()
        return jsonify({"success":True}), 200
    except Exception as e:
        return "An Error Occurred"
