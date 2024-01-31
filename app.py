from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)



@app.route('/diary')
def diary_list():
    all_diaries = Diary.query.all()
    return render_template('diary.html', all_diaries=all_diaries)

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


class Diary(db.Model):
    diaryId = db.Column(db.Integer, primary_key=True, autoincrement=True) # 시퀀스로 증가
    title = db.Column(db.String, nullable=False)
    editTime = db.Column(db.String, nullable=False)
    mainText = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Diary(diaryId={self.diaryId}, title='{self.title}', text='{self.mainText}')"

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
