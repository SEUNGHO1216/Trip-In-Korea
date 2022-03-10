#app.py
import pymongo
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
from pytz import timezone
from werkzeug.utils import secure_filename, redirect
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.okxdx.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/', methods=['GET'])
def home_get():
    token_receive = request.cookies.get('mytoken')
    # 로그인한 토큰이 있는 경우(로그인 완료한 유저)
    if token_receive != None:
        try:
            # 토큰으로 부터 payload를 불러옴
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            # 페이로드 내에 있는 userid를 변수에 할당
            userid = payload["id"]
            # 보여줄 정보 전부 끌어오기(최신순,내림차순)
            docs=list(db.test1.find({}).sort('_id', pymongo.DESCENDING))

            all_likes = db.likes.find({})
            like_count = {}
            like_by_me = {}

            for like in all_likes:
                # 좋아요를 누른 사람의 user id
                like_user_id = like["username"]
                # 현재 로그인한 사용자와, 게시글에 좋아요를 누른 사람이 동일하다면 해당 내역을 저장
                if userid == like_user_id:
                    like_by_me[like["post_id"]] = True
                # 게시글 마다 좋아요의 수를 저장
                try:
                    like_count[like["post_id"]] += 1
                except:
                    like_count[like["post_id"]] = 1

            for doc in docs:
                doc["_id"] = str(doc["_id"])
                # 현재 해당글의 좋아요 수가 몇개인지 적어라
                doc["count_heart"] = like_count[doc["_id"]] if doc["_id"] in like_count else 0
                # 내가 좋아요를 누른지의 유무
                doc["heart_by_me"] = True if doc["_id"] in like_by_me else False

            return render_template("mainpage.html", docs=docs, userid=userid) #메인페이지로 이동
        except jwt.ExpiredSignatureError:
            return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("signin_get", msg="로그인 정보가 존재하지 않습니다."))

    else: #로그인한 유저가 아닐 경우
        docs = list(db.test1.find({}).sort('_id', pymongo.DESCENDING))  # 보여줄 정보 전부 끌어오기
        return render_template("mainpage.html", docs=docs)  # 메인페이지로 이동

#마이페이지에 게시물 표현하는 메소드
@app.route('/user', methods=['GET'])
def user_get():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 토큰으로 부터 user id를 받아옴, 현재 로그인한 사용자가 누구인지 알 수 있다.
        userid = payload["id"]
        docs = list(db.test1.find({'userid': userid}).sort('_id', pymongo.DESCENDING))

        all_likes = db.likes.find({})
        like_count = {}
        like_by_me = {}

        for like in all_likes:
            like_user_id = like["username"]
            if userid == like_user_id:
                like_by_me[like["post_id"]] = True
            try:
                like_count[like["post_id"]] += 1
            except:
                like_count[like["post_id"]] = 1

        for doc in docs:
            print(doc)
            doc["_id"] = str(doc["_id"])
            # 현재 해당글의 좋아요 수가 몇개인지 적어라
            doc["count_heart"] = like_count[doc["_id"]] if doc["_id"] in like_count else 0
            # 내가 좋아요를 누른지의 유무
            doc["heart_by_me"] = True if doc["_id"] in like_by_me else False

        return render_template("user.html", docs=docs, userid=userid)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("signin_get", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login', methods=['GET'])
def signin_get():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 토큰이 유효할 경우 main 화면으로 이동
        return render_template("login.html")
    except jwt.ExpiredSignatureError:
        return render_template("login.html")
        # return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return render_template("login.html")
        # return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login', methods=['POST'])
def signin_post():
    # 로그인을 시도하는 사용자의 아이디
    userid_receive = request.form['userid_give']
    # 로그인을 시도하는 사용자의 패스워드
    userpassword_receive = request.form['userpassword_give']
    # 해쉬를 이용하여 사용자 비밀번호 암호화
    pw_hash = hashlib.sha256(userpassword_receive.encode('utf-8')).hexdigest()
    # 암호화한 비밀번호를 database에 저장
    result = db.test1User.find_one({"userid" : userid_receive, "userpassword" : pw_hash})

    # 회원 정보가 db에 존재하지 않을 경우
    if result is None:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

    # 회원 정보가 db에 존재할 경우
    payload = {
     'id': userid_receive,
     'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
    return jsonify({'result': 'success', 'token': token})

@app.route('/members/new', methods=['POST'])
def createAccount_post():
    # 사용자 계증 검증 부분은 post요청을 보내기 전 front 부분에서 이미 완료한 상태임
    # 회원 가입을 시도하는 사용자의 아이디
    userid_receive = request.form["userid_give"]
    # 회원 가입을 시도하는 사용자의 패스워드
    userpassword_receive = request.form['userpassword_give']
    # 사용자 패스워드 암호화
    pw_hash = hashlib.sha256(userpassword_receive.encode('utf-8')).hexdigest()
    # 회원가입을 시도하는 사용자의 닉네임
    username_receive = request.form['username_give']

    doc = {
        "userid" : userid_receive,
        "userpassword" : pw_hash,
        "username" : username_receive
    }
    # 데이터 베이스에 회원 정보 저장
    db.test1User.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/members/new', methods=['GET'])
def createAccount_get():
    return render_template("createAccount.html")


@app.route('/members/new/check_dup', methods=['POST'])
def check_duplicate_userId():
    # 회원 아이디 중복 확인
    # 데이터 베이스에서 회원 아이디가 존재하는지 확인하고
    # 중복 유무를 exists 변수에 담아서 반환
    userid_receive = request.form['userid_give']
    exists = bool(db.test1User.find_one({"userid": userid_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/write')
def write():
    token_receive = request.cookies.get('mytoken')
    print('토큰값', token_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('writing.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("signin_get", msg="로그인 정보가 존재하지 않습니다."))



@app.route('/writepage', methods=['POST'])
def write_post():
    # name_receive = 토큰의 id 를 이용하여 db 에서 이름 가져오기
    token_receive = request.cookies.get('mytoken')
    print('토큰값',token_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = payload["id"]


        img_receive = request.files["chooseFile"]
        print(img_receive)
        area_receive = request.form['area']
        comment_receive = request.form['comment_box']
        title_receive = request.form['title_box']
        img_name = secure_filename(img_receive.filename)

        print(userid,area_receive,comment_receive,img_name)
        today = datetime.now()
        # 파일 업로드
        filename=''
        if img_receive:
            mytime = today.strftime('%y-%m-%d-%H-%M-%S')
            filename = f'{mytime}.{img_name}'
            file_path='static/'
            img_receive.save(file_path + filename)

        doc = {
            "userid":userid,
            "img": filename,
            "area": area_receive,
            "title": title_receive,
            "comment": comment_receive,
            "pubdate": datetime.now(timezone('Asia/Seoul')).strftime('%y/%m/%d_%H:%M:%S')
        }
        db.test1.insert_one(doc)
        return redirect(url_for('home_get'))  # 게시글 추가 후 자연스럽게 메인페이지 이동

        # return render_template("home.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))

#메인페이지에서 지역 분류 요청이 들어올 시
@app.route('/sort')
def sortByArea():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = payload["id"]

        area=request.args.get('area') #GET방식으로 보낸 정보를 가져오는 코드
        print('area:',area)
        if area == "전체":
            docs = list(db.test1.find({}).sort('_id', pymongo.DESCENDING))  # db에서 지역 이름을 기준으로 해당 지역 전부 추출
            return render_template('mainpage.html', docs=docs, userid=userid)  # 메인페이지에 진자2 문법 활용을 위한 리스트변수 제공
        else:
            docs=list(db.test1.find({'area':area}).sort('_id',pymongo.DESCENDING)) #db에서 지역 이름을 기준으로 해당 지역 전부 추출
            return render_template('mainpage.html',docs=docs, userid=userid) #메인페이지에 진자2 문법 활용을 위한 리스트변수 제공
    except jwt.ExpiredSignatureError:
        return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("signin_get", msg="로그인 정보가 존재하지 않습니다."))

#마이페이지에서 지역 분류 요청이 들어올 시
@app.route('/sortMyPage')
def sortByAreaMyPage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = payload["id"]

        area=request.args.get('area') #GET방식으로 보낸 정보를 가져오는 코드
        print('area:',area)
        if area =="전체":
            docs=list(db.test1.find({'userid': userid}).sort('_id',pymongo.DESCENDING))  # db에서 지역 이름을 기준으로 해당 지역 전부 추출(해당 userdid값으로 필터링)
            return render_template('user.html', docs=docs, userid=userid)  # 마이페이지에 진자2 문법 활용을 위한 리스트변수 제공
        else:
            docs=list(db.test1.find({'userid':userid,'area':area}).sort('_id',pymongo.DESCENDING)) # db에서 지역 이름을 기준으로 해당 지역 전부 추출(해당 userid값으로 필터링)
            return render_template('user.html',docs=docs, userid=userid) #마이페이지에 진자2 문법 활용을 위한 리스트변수 제공
    except jwt.ExpiredSignatureError:
        return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("signin_get", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/update/<idx>',methods=["POST","GET"])
def update(idx):
    token_receive = request.cookies.get('mytoken')
    print('토큰값', token_receive)
    doc=db.test1.find_one({'_id':ObjectId(idx)})
    if request.method=="POST":
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            userid = payload["id"]
            img_text = request.form["chooseFile"] #수정 안하고 유지된 이미지
            img_receive = request.files["chooseFile2"] #수정하기 위해 새로 바꾼 이미지
            print(img_text,'/',img_receive)
            area_receive = request.form['area']
            comment_receive = request.form['comment_box']
            title_receive = request.form['title_box']
            img_name = secure_filename(img_receive.filename)
            today = datetime.now()
            # 파일 업로드
            filename = ''
            # 수정시 기존 파일을 다른 파일로 수정하는 경우
            if img_receive:
                mytime = today.strftime('%y-%m-%d-%H-%M-%S')
                filename = f'{mytime}.{img_name}'
                print(filename)
                file_path = 'static/'
                img_receive.save(file_path + filename)
            # 이미지 수정 안하고 기존거 유지하는 경우
            else:
                images = os.listdir('static/')
                print(images)
                if img_text in images:
                    print('doc[img]:',doc['img'])
                    filename=doc['img']
            doc = {
                "userid": userid,
                "img": filename,
                "area": area_receive,
                "title": title_receive,
                "comment": comment_receive,
                "pubdate": doc.get('pubdate'),
                "uptdate": datetime.now(timezone('Asia/Seoul')).strftime('%y/%m/%d_%H:%M:%S')
            }
            # idx값을 이용해 데이터베이스 수정
            db.test1.update_one({'_id':ObjectId(idx)},{'$set':doc})
            # 게시글 추가 후 자연스럽게 메인페이지 이동
            return redirect(url_for('home_get'))

        except jwt.ExpiredSignatureError:
            return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("signin_get", msg="로그인 시간이 만료되었습니다."))

    return render_template('update.html',doc=doc)

@app.route('/delete', methods=["POST"])
def delete():
    idx=request.form['idx']
    db.test1.delete_one({'_id':ObjectId(idx)})
    return redirect(url_for('home_get'))

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요를 누른 사람
        user_info = db.test1User.find_one({"userid": payload["id"]})
        # 글의 id
        post_id_receive = request.form["post_id_give"]
        # 좋아요
        type_receive = request.form["type_give"]
        # 행위 (좋아요 상태 : 좋아요가 눌려져 있는 상태인지 , 눌려져 있지 않은 상태인지)
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["userid"],
            "type": type_receive
        }
        # 좋아요가 눌러져 있지 않는 상태라면 (db에서 좋아요 정보를 넣는다.)
        if action_receive == "like":
            db.likes.insert_one(doc)
        # 좋아요가 눌러져 있는 상태라면 (db에서 좋아요 정보를 지운다.)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home_get"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

