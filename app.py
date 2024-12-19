from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_json import FlaskJSON, json_response, as_json, JsonError
from flask_login import login_user, login_required, UserMixin, LoginManager, current_user, logout_user


app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FinalProject_CS250'
app.config['SECRET_KEY'] = 'Secret Key'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_user():
        return User.query.all()

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String)
    model = db.Column(db.String)
    price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_car():
        return Car.query.all()


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/')
def main():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        return render_template('index.html', auth=True, user=user)
    else:
        return render_template('index.html', auth=False)


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'GET':
        return render_template('create.html', error=False)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User()
            user.username = username
            user.password = password

            user.insert()
            login_user(user)
            return redirect('/')
        else:
            return render_template('create.html', error=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'GET':
        return render_template('login.html', error=False)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user is None:
            return render_template('login.html', error=True)
        if user.password == password:
            login_user(user)
            return redirect('/')
        else:
            return render_template('login.html', error=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    if request.method == 'GET':
        return render_template('add_car.html')
    elif request.method == 'POST':
        data = request.get_json()
        brand = data.get('brand')
        model = data.get('model')
        price = data.get('price')

        new_car = Car(
            brand=brand,
            model=model,
            price=price,
            user_id=current_user.id
        )
        new_car.insert()
        return {'message': 'Car Added Successfully'}


@app.route('/view_cars')
@login_required
def view_cars():
    cars = Car.get_car()
    users = User.get_user()
    return render_template('view.html', cars=cars, users=users, current_user_id=current_user.id)


@app.route('/update/<car_id>', methods=['GET', 'POST'])
@login_required
def update(car_id):
    car = Car.query.filter_by(id=car_id, user_id=current_user.id).first()
    if not car:
        return render_template('error.html', err=1)

    if request.method == 'GET':
        return render_template('update.html', car=car)

    elif request.method == 'POST':
        car.brand = request.form['brand']
        car.model = request.form['model']
        car.price = request.form['price']
        db.session.commit()
        return redirect('/view_cars')


@app.route('/delete/<car_id>', methods=['GET'])
@login_required
def delete(car_id):
    car = Car.query.filter_by(id=car_id, user_id=current_user.id).first()
    if not car:
        return render_template('error.html', err=1)

    db.session.delete(car)
    db.session.commit()
    return redirect('/view_cars')


@app.errorhandler(404)
def err404(err):
    return render_template('error.html', err=404)

@app.errorhandler(401)
def err401(err):
    return render_template('error.html', err=401)


app.run(debug=True)