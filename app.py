from flask import Flask, request
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token




app = Flask(__name__) # Name of app should be same as that of project name
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super secret' #change this in real life (it should be some uid or secret string)


db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Created')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Dropped!')


@app.cli.command('db_seed')
def db_seed():

    test_user1 = User(card_number= 1234567891234567,
                     first_name='Test',
                     last_name='user1',
                     email='test@test.com',
                     password='P@sswo0rd',
                     address='56, xYZ STREET,iNDIA')
    
    db.session.add(test_user1)
    db.session.commit()
    print('Database Seeded!')


@app.route('/')  # Root endpoint/url returning hello world .
def hello_world():
    return 'Hello World!'





@app.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='Email already registered!'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='Registration successful'), 201


@app.route('/login',methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message ='Login Successful!',access_token=access_token)
    else:
        return jsonify(message='Invalid credentials!'), 401


#database models
class User(db.Model):
    __tablename__ = 'users'
    card_number = Column(Integer,primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String,unique=True)
    password = Column(String)
    address = Column(String)


class Userschema(ma.Schema):
    class Meta:
        fields=('card_number', 'first_name', 'last_name', 'email', 'password', 'address')



user_schema = Userschema()
users_schema = Userschema(many=True)



if __name__ == 'main':
    app.run()