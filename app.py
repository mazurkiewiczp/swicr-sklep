# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for, render_template, abort, request, session
import string, os, sys, math, time, json
from os import environ
from sqlalchemy import create_engine, Table
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from database import User, Base, Item, Order
from flask import request
from sqlalchemy.sql.expression import func, select

app = Flask(__name__)
engine = create_engine('sqlite:///app.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
sessiondb = DBSession()
app.secret_key = os.urandom(24)


from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('server.key')
context.use_certificate_file('server.crt')

def checkUser(login, password):
    usertmp = sessiondb.query(User).filter(User.username == login).first()
    if usertmp is None:
        return False
    return usertmp.check_password(password)

@app.route('/index.html', methods=['GET', 'POST'])
@app.route('/')
def index():
    if 'login' in session:
        return render_template('index.html', user=session['login'], data=sessiondb.execute('SELECT * from items;'))
    return render_template('login.html', info='')

@app.route('/zaloguj', methods=['GET', 'POST'])
def zaloguj():
    if 'login' in session:
        return index()
    return render_template('login.html', info='')

@app.route('/login', methods=['GET', 'POST'])
def verification():	
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
    if checkUser(login, password):
        session['login'] = login
        return index()
    return render_template('login.html', info=u'Niepoprawne dane logowania')

@app.route('/signUp', methods=['GET', 'POST'])
def display_registration():
    return render_template('signUp.html', info='')

@app.route('/register', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        password2 = request.form['password_repeat']
        mail = request.form['mail']
    if login == '' or password == '' or mail == '':
        return render_template('signUp.html', info=u'Wypelnij wszystkie pola')
    if not password2 == password:
        return render_template('signUp.html', info=u'Hasła się nie zgadzają')
    usertmp = sessiondb.query(User).filter(User.username == login).first()
    if not usertmp is None:
        return render_template('signUp.html', info=u'Niepoprawne dane')
    new_user = User(login,password,mail)
    sessiondb.add(new_user)
    sessiondb.commit()
    return render_template('login.html', info=u'Rejestracja udana')

@app.route('/koszyk')
def koszyk():
    if 'login' in session:
        login = session['login']
        return render_template('koszyk.html', data=sessiondb.execute('select orders.item_id, items.name, items.price, count(orders.item_id) as liczba from orders join items on orders.item_id=items.id where orders.user_id = :val group by item_id;', {'val':login}))
    return render_template('login.html')

@app.route('/koszyk_dodaj/<int:item_id>')
def koszyk_dodaj(item_id):    
        sessiondb.add(Order(item_id, session['login']))
        sessiondb.commit()
        login = session['login']
        return render_template('koszyk.html', data=sessiondb.execute('select orders.item_id, items.name, items.price, count(orders.item_id) as liczba from orders join items on orders.item_id=items.id where orders.user_id = :val group by item_id;', {'val':login}))

@app.route('/koszyk_usun/<int:item_id>')
def koszyk_usun(item_id):    
        login = session['login']
        sessiondb.execute('delete from orders where orders.item_id = :iid and orders.user_id = :val limit 1;',{'iid': item_id, 'val': login})
        sessiondb.commit()
        login = session['login']
        return render_template('/koszyk.html', data=sessiondb.execute('select orders.item_id, items.name, items.price, count(orders.item_id) as liczba from orders join items on orders.item_id=items.id where orders.user_id = :val group by item_id;', {'val':login}))

@app.route('/profil')
def profil():
    if 'login' in session:
        return render_template('profil.html')
    return render_template('login.html', info='')

@app.route('/dalej')
def dalej():
    if 'login' in session:
        return render_template('dalej.html')
    return render_template('login.html', info='')

@app.route('/zamow', methods=['GET', 'POST'])
def zamow():
    if 'login' in session:
        suma = 0
        orderData = ''
        login = session['login']
        if request.method == 'POST':
            dostawa = str(request.form['iin']) + ' ' + str(request.form['ulica']) + ' ' + str(request.form['nr']) + ' ' + str(request.form['miasto']) + ' ' + str(request.form['kod']) + ' ' + str(request.form['telefon'])
        else:
            dostawa = 'odbior osobisty'
        data=sessiondb.execute('select orders.item_id, items.name, items.price, count(orders.item_id) as liczba from orders join items on orders.item_id=items.id where orders.user_id = :val group by item_id;', {'val':login})
        for it in data:
            suma += int(it[2])*int(it[3])
            orderData += str(it[0]) + ' ' + str(it[2]) + ' ' + str(it[3]) + ' '
        session['time'] = time.time()
        f = open('orders.txt', 'r+')
        notes = json.load(f)
        date = time.strftime("%c")
        new = {'user': str(login), 'order': str(orderData), 'dostawa': str(dostawa), 'date': str(date)}
        notes.insert(0, new)
        f.close()
        f = open('orders.txt', 'w')
        json.dump(notes, f)
        f.close()
        sessiondb.execute('delete from orders where orders.user_id = :val;',{'val': login})
        sessiondb.commit()
        return render_template('zamowienie.html',suma=suma)
    return render_template('login.html', info='')

@app.route('/oplata')
def oplata():
    if 'login' in session:
        if (time.time() - session['time']) < 10:
            return render_template('oplata.html',info="Zamowienie oplacone pomyslnie")
        return render_template('oplata.html',info="Minal czas na oplacenie zamowienia. Zamowienie anulowane.") 
    return render_template('login.html', info='')

@app.route('/changePassword', methods=['GET', 'POST'])
def display_changePassword():
    login = session['login']
    return render_template('changePassword.html', name=login)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    login = session['login']
    if request.method == 'POST':
        password = request.form['oldpassword']
        newpassword = request.form['newpassword']
        newpassword_repeat = request.form['newpassword_repeat']
    usertmp = sessiondb.query(User).filter(User.username == login).first()
    if not newpassword == newpassword_repeat:
        return render_template('changePassword.html', info='Hasla sie nie zgadzaja')
    if usertmp.check_password(password):
        usertmp.set_password(newpassword)
        sessiondb.commit()
        info = u'Haslo zmienione'
        return render_template('profil.html', info=info)
    return render_template('changePassword.html', info='Niepoprawne dane')

@app.route('/logout')
def logout():
    session.pop('login', None)
    return index()

context = ('server.crt', 'server.key')
app.run(ssl_context=context)
