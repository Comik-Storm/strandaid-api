import os
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, render_template, Response, request
import json
from azure.storage.blob import BlobServiceClient

#Setup Blob Storage
key = "dWyL0uCfyrNgfI1u8oiVKmnams4rqIEcd5viAfLTBKtt9xx1meq0zTU7J66VE3HdK8wuQmP0o/zt+AStgA2y0A=="
conn = "DefaultEndpointsProtocol=https;AccountName=strandaidobjects;AccountKey=dWyL0uCfyrNgfI1u8oiVKmnams4rqIEcd5viAfLTBKtt9xx1meq0zTU7J66VE3HdK8wuQmP0o/zt+AStgA2y0A==;EndpointSuffix=core.windows.net"
account = "strandaidobjects"
container = "strandaidobjectcaptures"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

#Setup Client
bsc = BlobServiceClient.from_connection_string(conn)

#Setup Google Firebase
cred = credentials.Certificate('./key.json')
firebase = initialize_app(cred)

#Setup Firestore DB
db = firestore.client()
records = db.collection('records')
drones = db.collection('captures')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "Hello From Team Strandaid!"


@app.route('/objects', methods=['POST'])
def objects():
    try:
        if 'file' not in request.files:
            return "File Not Found!"
        file = request.files['file']
        filename = file.filename
        file.save(filename)
        blob_client = bsc.get_blob_client(container=container, blob=filename)
        data = json.loads(request.form.get('data'))
        with open(filename, "rb") as data:
                try:
                    blob_client.upload_blob(data, overwrite=True)
                except:
                    pass
        newData = {
                "imageBy": data["imageBy"],
                "imgUrl": "https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}".format(storage_account_name=account, container_name=container, blob_name=filename),
                "lat": data["lat"],
                "long": data["long"],
                "object": data["object"],
                "time": data["time"]
                }
        os.remove(filename)
        drones.add(newData)
        return jsonify({"success": True}), 200
    except Exception as e:
        return "An Error Occurred"



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
