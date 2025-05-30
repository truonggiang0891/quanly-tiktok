from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

# Model Account ở trên

# ... các route khác ...

@app.route('/import', methods=['GET', 'POST'])
def import_accounts():
    if request.method == 'POST':
        bulkdata = request.form.get('bulkdata', '')
        lines = bulkdata.strip().split('\n')
        count = 0
        for line in lines:
            if not line.strip():
                continue
            data = parse_account_line(line)
            acc = Account(
                tiktok_id=data["tiktok_id"],
                password=data["password"],
                email=data["email"],
                email_password=data["email_password"],
                cookie=data["cookie"]
            )
            db.session.add(acc)
            count += 1
        db.session.commit()
        return render_template("import_done.html", count=count)
    return render_template('import.html')

def parse_account_line(line):
    fields = line.strip().split('|')
    while len(fields) < 5:
        fields.append("")  # Tự động bổ sung chuỗi rỗng nếu thiếu trường
    return {
        "tiktok_id": fields[0],
        "password": fields[1],
        "email": fields[2],
        "email_password": fields[3],
        "cookie": fields[4],
    }



# Thêm trường tiktok_id, password, email, email_password, cookie
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tiktok_id = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))
    email_password = db.Column(db.String(100))
    cookie = db.Column(db.Text)
    # Các trường khác vẫn giữ nguyên nếu cần (market, code, v.v.)
    # ...



@app.route('/')
def index():
    accounts = Account.query.all()
    return render_template('index.html', accounts=accounts)

@app.route('/add', methods=['POST'])
def add_account():
    acc = Account(
        market=request.form['market'],
        code=request.form['code'],
        status=request.form['status'],
        channel_name=request.form['channel_name'],
        follow=request.form['follow'],
        like=request.form['like'],
        view=request.form['view'],
        link=request.form['link'],
        user=request.form['user'],
        password=request.form['password'],
        mail=request.form['mail'],
        pass_mail=request.form['pass_mail'],
        cookies=request.form['cookies'],
        post_schedule=request.form['post_schedule'],
        note=request.form['note']
    )
    db.session.add(acc)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_account(id):
    acc = Account.query.get(id)
    db.session.delete(acc)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export():
    accounts = Account.query.all()
    df = pd.DataFrame([{
        'market': a.market,
        'code': a.code,
        'status': a.status,
        'channel_name': a.channel_name,
        'follow': a.follow,
        'like': a.like,
        'view': a.view,
        'link': a.link,
        'user': a.user,
        'password': a.password,
        'mail': a.mail,
        'pass_mail': a.pass_mail,
        'cookies': a.cookies,
        'post_schedule': a.post_schedule,
        'note': a.note
    } for a in accounts])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="accounts.xlsx", as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

def parse_account_line(line):
    # Chuẩn hóa và bổ sung đủ 5 trường
    fields = line.strip().split('|')
    while len(fields) < 5:
        fields.append("")
    return {
        "tiktok_id": fields[0],
        "password": fields[1],
        "email": fields[2],
        "email_password": fields[3],
        "cookie": fields[4],
    }
