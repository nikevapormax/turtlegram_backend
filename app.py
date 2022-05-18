from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, abort, jsonify, request
import hashlib
import json
from flask_cors import CORS
import jwt

# decorator 함수를 사용해 사용자의 토큰값 확인


def authorize(f):
    @wraps(f)
    def decorated_function():
        # 만약 Authorization이 헤더 안에 없다면
        if not 'Authorization' in request.headers:
            abort(401)  # 401 에러를 반환
        # Authorization이 헤더 안에 있다면 'token' 변수에 저장
        token = request.headers['Authorization']
        try:
            # 토큰을 디코드한 값을 user에 저장
            # _id, email, exp가 들어있음
            user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            abort(401)
        return f(user)
    return decorated_function


app = Flask(__name__)
# 현재는 테스트 서버에서 돌려서 origins에 모든 것을 다 받아오는 *를 썼지만, 나중에 서비스를 하게 된다면 원하는 프론트에서만 받도록 설정해야 함
cors = CORS(app, resources={r"*": {"origins": "*"}})
client = MongoClient('localhost', 27017)
db = client.turtle

SECRET_KEY = 'turtle'


@app.route("/")
@authorize
def home(user):
    print(user)
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

    return jsonify({'msg': 'Signup success! Welcome!'}), 201


@app.route("/signin", methods=['POST'])
def sign_in():
    data = json.loads(request.data)
    my_email = data.get('email')
    password_receive = data.get('password')
    my_pw = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    my_signin = db.user.find_one({'email': my_email, 'password': my_pw})
    print(my_signin)

    if my_signin is not None:
        payload = {
            'id': str(my_signin['_id']),
            'email': my_email,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        print(payload)
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # 발급받은 token을 user db의 해당 유저에게 할당
        db.user.update_one({'email': my_email}, {'$set': {'token': token}})
        return jsonify({'msg': 'Login success! Welcome!', 'token': token}), 201
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route("/getuserinfo", methods=['GET'])
@authorize
def get_user_info(user):

    user_info = db.user.find_one({'_id': ObjectId(user['id'])})
    print('3', user_info)

    return jsonify({'msg': 'success', 'email': user_info['email']})


@app.route("/article", methods=['POST'])
@authorize
def post_article(user):
    data = json.loads(request.data)
    print(data)

    # 여기서의 user는 authorize에 들어가는 인자값
    # user에는 payload로 만들어진 token이 존재하고, payload에는 사용자의 str화 시킨 _id가 존재한다.
    # 이 값을 mongoDB에서 사용하기 위해서는 다시 ObjectId로 변환해줘야 하기 때문에 아래와 같은 작업 진행
    db_user = db.user.find_one({'_id': ObjectId(user.get('id'))})

    # 현재 시각 표시
    now_date = datetime.datetime.now().strftime('%H : %M : %S')

    doc = {
        'title': data.get('title', None),  # 현재는 None 처리를 통해 값이 없더라도 입력 가능
        # 추후 값이 없을 때 에러 처리하는 것을 만들어 활용해보기
        'content': data.get('content', None),
        'user': user['id'],
        'user_email': db_user['email'],
        'time': now_date
    }
    print(doc)
    db.article.insert_one(doc)
    return jsonify({'msg': 'success'})


@app.route('/article', methods=['GET'])
def get_article():
    articles = list(db.article.find())

    # articles의 모든 _id의 값을 str화해야 json 형식으로 보낼 수 있기 때문에 해당 작업 진행
    for article in articles:
        article['_id'] = str(article['_id'])

    return jsonify({'msg': 'success', 'articles': articles})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
