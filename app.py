from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, abort, jsonify, request
import hashlib
import json
from bson.json_util import loads, dumps
from flask_cors import CORS
import jwt

# decorator 함수를 사용해 사용자의 토큰값 확인


def authorize(f):
    @wraps(f)
    # argument와 key-word argument가 같이 들어가는 경우를 위해 작성
    # *과 ** 만 있다면 이름은 뒤에 아무거나 붙어도 무방은 함
    # *args: list 형태로 아무거나 다 들어와 된다.
    # **kwargs : a = b의 형태로 즉, 키워드의 형태로 몇개씩 들어와도 인식을 하겠다.
    def decorated_function(*args, **kwargs):
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
        return f(user, *args, **kwargs)
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

    return jsonify({'msg': 'Signup success! Welcome!'})


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
    # 여기에는 token을 decode하고 나온 3가지 값이 있다. : _id, email, exp
    user_info = db.user.find_one({'_id': ObjectId(user['id'])})
    print('3', user_info)

    # id 값을 반환받아 삭제하기 버튼을 로그인한 사용자가 작성한 글에서만 보일 수 있도록 조치함
    return jsonify({'msg': 'success', 'email': user_info['email'], 'id': user['id']})


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
    now_date = datetime.now().strftime('%H : %M : %S')

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


@app.route('/article/<article_id>', methods=["GET"])
def get_article_detail(article_id):
    # 위의 get_article 에서 json 형식으로 데이터를 보내기 위해 _id 값을 str화 하였으니, db에서 해당 값을 찾을 땐 꼭 ObjectId화 해야한다.
    article = db.article.find_one({'_id': ObjectId(article_id)})
    comments = list(db.comment.find({"article": article_id}))
    print(article)

    if article:
        # 다시 _id를 str화 해주면서 모든 article에 담겨 있는 값을 json형식으로 반환할 수 있게 해준다.
        article['_id'] = str(article['_id'])
        # dumps -> ObjectId를 json화 해주는 기능
        article['comments'] = json.loads(dumps(comments))
        return jsonify({'msg': 'success', 'article': article})
    else:
        return jsonify({'msg': 'fail'}), 404


@app.route('/article/<article_id>', methods=["PATCH"])
@authorize
def patch_article_detail(user, article_id):
    data = json.loads(request.data)

    # 게시글을 변경하게 되면 제목과 내용만 바뀌니까 그 둘을 data에서 뽑아온다.
    title = data.get("title")
    content = data.get("content")

    # filter 값으로 게시글의 고유값인 옵젝아이디, 그리고 해당 글을 작성한 유저를 찾아야 하므로 authorize의 user에 들어있는 id 값을 사용한다.
    # 여기서 잠깐! 왜 유저의 아이디는 옵젝아이디가 아니죠? -> article db에는 유저의 아이디가 string으로 저장되어 있다. 물론 user db에서 값을 빼온다하면 옵젝아이디로 빼야함!
    article = db.article.update_one(
        {"_id": ObjectId(article_id), "user": user["id"]}, {"$set": {"title": title, "content": content}})

    # 위의 업데이트가 성공적으로 이루어졌다면 1이 출력되고, 아니라면 0이 출력됨
    print(article.matched_count)

    # 이곳 POSTMAN 사용법 :
    # 해당 게시글의 아이디를 찾고, url에 넣어준다. 이러고 보내보면 오류가 난다. 왜냐? authorization에 글쓴이의 정보가 없기 때문이다.
    # 아예 _id 값이 불분명하다고 생각된다면 다음과 같이 처음부터 시작하자
    # /signin -> _id 추출 -> /get_articles -> 게시글의 _id 추출 -> /get_article_detail -> 게시글의  _id 값을 넣어 정보 확인
    # -> patch_article로 가 Headers에 Authorization 값을 넣어줌(사용자의 _id값) -> send -> 'msg': 'success' -> app.py로 와서 article.matched_count 확인
    if article.matched_count:
        return jsonify({'msg': 'success'})
    else:
        return jsonify({'msg': 'fail'}), 403


@app.route('/article/<article_id>', methods=["DELETE"])
@authorize
def delete_article_detail(user, article_id):
    article = db.article.delete_one(
        {"_id": ObjectId(article_id), "user": user['id']})

    # 위의 수정하기 경우와 똑같다. 게시글이 없거나 다른사람의 글을 지우려 하거나 한다면 0이 출력되고, 똑바로 접근했다면 1이 나온다.
    if article.deleted_count:
        return jsonify({'msg': 'success'})
    else:
        return jsonify({'msg': 'fail'}), 403


# 댓글 달기 기능
@app.route('/article/<article_id>/comment', methods=['POST'])
@authorize
def post_comment(user, article_id):
    data = json.loads(request.data)
    print("댓글달기", data)

    db_user = db.user.find_one({'_id': ObjectId(user.get('id'))})
    now = datetime.now().strftime("%H:%M:%s")
    doc = {
        'article': article_id,
        'content': data.get('content', None),
        'user': user['id'],
        'user_email': db_user['email'],
        'time': now
    }
    print(doc)

    db.comment.insert_one(doc)
    return jsonify({'msg': 'success'})


@app.route('/article/<article_id>/comment', methods=['GET'])
def get_comment(article_id):
    comments = list(db.comment.find({"article": article_id}))
    json_comments = json.loads(dumps(comments))
    return jsonify({'msg': 'success', 'comments': json_comments})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
