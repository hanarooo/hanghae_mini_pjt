from flask import Flask, render_template, request, redirect, url_for, jsonify, json, session
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from json.decoder import JSONDecodeError


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'session_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


# 다이어리 시작
@app.route('/diary')
def diary_list():
    all_diaries = Diary.query.all()
    return render_template('diary.html', all_diaries=all_diaries)

@app.route('/search')
def search():
    data = []
    # URL에서 'query' 파라미터를 가져옵니다.
    query = request.args.get('query', '').lower()
    # 검색어에 해당하는 자료를 찾습니다.
    search_results = [item for item in data if query in item['title'].lower()]

    return render_template('search_results.html', query=query, results=search_results)


@app.route('/diary/regist', methods=['GET', 'POST'])
def diary_regist():
    if request.method == 'POST':
        title = request.form.get('title')
        main_text = request.form.get('mainText')
        edit_time = datetime.now().strftime('%Y-%m-%d')

        diary = Diary(title=title, mainText=main_text, editTime=edit_time)
        db.session.add(diary)
        db.session.commit()

        return redirect(url_for('diary_list'))

    return render_template('diary_regist.html')


@app.route('/diary/<num>', methods=['GET', 'POST'])
def diary_detail(num):
    diary = Diary.query.get_or_404(num)

    if request.method == 'POST':
        new_title = request.form['title']
        new_main_text = request.form['mainText']

        diary.title = new_title
        diary.mainText = new_main_text
        db.session.commit()

        return redirect(url_for('diary_list'))

    return render_template('diary_detail.html', diary=diary)


@app.route('/diary/delete/<diaryId>', methods=['post'])
def delete_diary(diaryId):
    diary = Diary.query.get_or_404(diaryId)
    db.session.delete(diary)
    db.session.commit()
    return jsonify({'success': True, 'redirect': url_for('diary_list')})


class Diary(db.Model):
    diaryId = db.Column(db.Integer, primary_key=True,
                        autoincrement=True)  # 시퀀스로 증가
    title = db.Column(db.String, nullable=False)
    editTime = db.Column(db.String, nullable=False)
    mainText = db.Column(db.Text)

    def __repr__(self):
        return f"Diary(diaryId={self.diaryId}, title='{self.title}', text='{self.mainText}', editTime='{self.editTime}')"


# 회원가입 및 로그인
class Member(db.Model):
    memberId = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pwd = db.Column(db.String, nullable=False)


def __repr__(self):
    return f"Member(memberId={self.memberId}, name='{self.name}', pwd='{self.pwd}')"

# 로그인
@app.route('/signIn', methods=['GET', 'POST'])
def sign_in():
    checkId = None
    checkPw = None

    if request.method == 'POST':
        checkId = request.form.get('memberId')
        checkPw = request.form.get('pwd')

        member = Member.query.filter_by(
            memberId=checkId, pwd=checkPw).first()
        print(member.memberId)
        if member:
            # 로그인 성공 시 세션에 사용자 정보 저장
            session['memberId'] = checkId
            return redirect(url_for('dashboard'))
        else:
            return render_template('signin.html', msg='아이디 또는 비밀번호를 확인해 주세요')

    return render_template('signin.html')

##############################################################################################
# 대시보드 페이지 - 로그인이 필요한 페이지

@app.route('/dashboard')
def dashboard():
    if 'memberId' in session:
        # 세션에 사용자 정보가 있다면 index 화면을 렌더링
        return render_template('index.html', memberId=session['memberId'])
    else:
        # 세션에 사용자 정보가 없다면 로그인 화면으로 리다이렉트
        return redirect(url_for('sign_in'))

# 로그아웃
@app.route('/logout')
def logout():
    # 세션에서 사용자 정보 삭제
    session.pop('memberId', None)
    return redirect(url_for('sign_in'))
###############################################################################################

# 회원가입
@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        newId = request.form.get('newId')
        newPwd = request.form.get('newPwd')
        newName = request.form.get('newName')

        new_member = Member(memberId=newId, name=newName, pwd=newPwd)
        db.session.add(new_member)
        db.session.commit()

        # 회원가입 성공 후 signin.html로 이동
        return redirect(url_for('sign_in'))

    return render_template('signup.html')


@app.route('/check', methods=['POST'])
def check_duplicate():
    if request.method == 'POST':
        data = request.get_json()
        newId = data.get('newId')

        oldMember = Member.query.filter_by(memberId=newId).first()

        if oldMember:
            print('duplicate')
            return jsonify({'result': 'duplicate'})
        else:
            print('success')
            return jsonify({'result': 'success'})
    return render_template('signup.html')


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
