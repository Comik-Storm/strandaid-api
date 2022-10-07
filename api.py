from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, render_template, Response, request


#Setup Google Firebase
cred = credentials.Certificate('key.json')
firebase = initialize_app(cred)

#Setup Firestore DB
db = firestore.client()
records = db.collection('records')

app = Flask(__name__)



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