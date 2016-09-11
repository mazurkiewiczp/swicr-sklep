import bcrypt, time
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    pw_hash = Column(String(120))
    mail = Column(String(30))
    adres = Column(String(80))

    def __init__(self, username, password, mail):
        self.username = username
        self.set_password(password)
	self.set_mail(mail)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
	self.pw_hash = bcrypt.hashpw(self.pw_hash.encode('utf-8'), salt)

    def check_password(self, password):
        return bcrypt.hashpw(bcrypt.hashpw(password.encode('utf-8'), self.pw_hash.encode('utf-8')), self.pw_hash.encode('utf-8')) == self.pw_hash.encode('utf-8')

    def set_mail(self, mail):
        self.mail = mail

    def set_adres(self, mail):
        self.adres = adres


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    price = Column(Integer)
    quantity = Column(Integer)

    def __init__(self, name, price):
        self.name = name
        self.set_price(price)

    def __repr__(self):
        return '<Item %r>' % self.name

    def set_price(self, price):
        self.price = price

    def set_quantity(self, quantity):
        self.quantity = quantity


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)

    def __init__(self, item_id):
        self.item_id = item_id

    def __repr__(self):
        return '<Order %r>' % self.id

    def set_item_id(self, item_id):
        self.item_id = item_id

