from flask import Flask, make_response, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# sesi in-memori ajah
sessions = {
    "PRESERVED-ADMIN-1": {
        "username": "admin",
        "password": "admin", # tinggal hash jika produksi
    },
    "PRESERVED-ADMIN-2": {
        "username": "monyet",
        "password": "monyet", # tinggal hash jika produksi
    },
}

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    return """
<html>
<body>
    <p>Selamat datang!</p>
    <ul>
        <li><a href=\"/login\">Login</p></li>
        <li><a href=\"/logout\">Logout</p></li>
        <li><a href=\"/students\">Dashboard</p></li>
    </ul>
</body>
</html>
"""

@app.route('/logout')
def logout():
    resp = redirect(url_for('index'))
    resp.delete_cookie("token")
    return resp

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == "GET":
        return """
<html>
<body>
    <p>Login</p>
    <form action="/login" method="POST">
        <input required="1" name="username" placeholder=\"username\" />
        <input required="1" name="password" placeholder=\"password\" />
        <button type="submit">submit</button>
    </form>
</body>
</html>
"""

    resp = make_response(redirect(url_for('list_students')))

    for k, v in sessions.items():
        if v["username"] == request.form.get("username") and \
           v["password"] == request.form.get("password"):
            resp.set_cookie("token", k)

    return resp

@app.route('/students')
def list_students():
    if not (request.cookies.get("token") in sessions):
        return """
<html>
<body>
    <img src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimages-cdn.9gag.com%2Fphoto%2Fam8bmwX_700b.jpg&f=1&nofb=1&ipt=e23c3e7ba5bfff1a6f62ab980dcf9ed8b25fd14ace46e3ae94adebc40e6375f5&ipo=images" width="200" height="200" />
    <p>Ga bole yaa</p>
</body>
</html>
"""

    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    if not (request.cookies.get("token") in sessions):
        return {} # lempar kode 401 unauthorized jika perlu

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>') 
def delete_student(id):
    if not (request.cookies.get("token") in sessions):
        return {} # lempar kode 401 unauthorized jika perlu

    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if not (request.cookies.get("token") in sessions):
        return {} # lempar kode 401 unauthorized jika perlu

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # RAW Query
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

