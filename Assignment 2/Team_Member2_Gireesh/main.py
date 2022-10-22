
from flask import Flask, render_template, request, redirect, url_for, session
import re

app = Flask(__name__)
app.secret_key = 'PNT2022TMID47221'
try:
	# Local Mysql Server
    import mysql.connector
    connection = mysql.connector.connect(host ='localhost',database = 'ibmsample', user = 'root', password = 'root',auth_plugin='mysql_native_password')
    if connection.is_connected():
        print("Server Details : ", connection.get_server_info())
    if connection:
        cursor = connection.cursor()
        qry =   """CREATE TABLE IF NOT EXISTS `accounts` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `username` varchar(50) NOT NULL,
                        `password` varchar(255) NOT NULL,
                        `email` varchar(100) NOT NULL,
                        PRIMARY KEY (`id`)
                        ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
                """
        cursor.execute (qry)  

except Exception as e:
    print(e)
    print("Sorry! MySQL Connection Fail... ")

@app.route('/')
@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = connection.cursor()
		try:
			cursor.execute('SELECT * FROM accounts WHERE username = %s', (username, ))
			account = cursor.fetchone()
		except Exception as e :
			account = None
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			print(email,username,password)
			#cursor.execute('INSERT INTO accounts VALUES (%s,% s, % s, % s)', ("null",username, password, email, ))
			cursor.execute('INSERT INTO accounts VALUES (null,"root","P@sssw0rd","root@gmail.com")')
			connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = connection.cursor()
		cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account[0]
			session['username'] = account[1]
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))
app.run()
