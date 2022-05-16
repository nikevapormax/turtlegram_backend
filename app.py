from pymongo import MongoClient
from flask import Flask, jsonify, request
import hashlib
import json
from flask_cors import CORS


app = Flask(__name__)
# 현재는 테스트 서버에서 돌려서 origins에 모든 것을 다 받아오는 *를 썼지만, 나중에 서비스를 하게 된다면 원하는 프론트에서만 받도록 설정해야 함
cors = CORS(app, resources={r"*": {"origins": "*"}})
client = MongoClient('localhost', 27017)
db = client.turtle


@app.route("/")
def home():
    return jsonify({'msg': 'success'})


@app.route("/signup", methods=['POST'])
def sign_up():
    # JSON 형식으로 데이터 받음
    data = json.loads(request.data)

    email_receive = data.get('email')
    domain = ['naver.com', 'gmail.com', 'daum.net']
    if '@' in email_receive:
        if email_receive.split('@')[1] in domain:
            if db.user.find_one({'email': email_receive}):
                return jsonify({'msg': '이미 존재하는 이메일입니다.'})
            else:
                email = email_receive
        else:
            return jsonify({'msg': '도메인을 확인해주세요.'})
    elif email_receive == '':
        return jsonify({'msg': '이메일 칸이 비었습니다.'})
    else:
        return jsonify({'msg': '이메일 형식으로 입력바랍니다.'})

    password_receive = data.get('password')
    if password_receive == '':
        return jsonify({'msg': '비밀번호를 입력해주시기 바랍니다.'})
    else:
        password_hash = hashlib.sha256(
            password_receive.encode('utf-8')).hexdigest()

    doc = {
        'email': email,
        'password': password_hash
    }
    db.user.insert_one(doc)

    return jsonify({'msg': 'Signup success! Welcome!'})


@app.route("/login", methods=['POST'])
def log_in():
    return jsonify({'msg': 'Login success! Welcome!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
