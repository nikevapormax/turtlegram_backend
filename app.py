import json
from flask import Flask, jsonify, request
from flask_cors import CORS

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.turtle

app = Flask(__name__)
# 현재는 테스트 서버에서 돌려서 origins에 모든 것을 다 받아오는 *를 썼지만, 나중에 서비스를 하게 된다면 원하는 프론트에서만 받도록 설정해야 함
cors = CORS(app, resources={r"*": {"origins": "*"}})


@app.route("/")
def home():
    return jsonify({'message': 'success'})


@app.route("/signup", methods=['POST'])
def sign_up():
    data = json.loads(request.data)

    email_receive = data.get('email')
    password_receive = data.get('password')

    print(data.get('email'), data['password'])
    # print(request.form['id']) 으로 쓰게 되면 만약 값이 없을 때 error가 발생하고, 이는 server에게 안 좋음
    # 따라서 아래의 request.form.get('id')을 사용해 만약 값이 없다면 None 값을 받는 것이 나음
    # print(request.form.get('id'))

    doc = {
        'email': email_receive,
        'password': password_receive
    }
    db.signup.insert_one(doc)
    return jsonify({'message': 'success2'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
