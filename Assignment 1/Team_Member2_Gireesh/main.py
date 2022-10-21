from urllib.request import urlopen
from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/resume_template')
def resume_template():
    return render_template("resume_template.html")

@app.route('/create')
def create():
    return "<h1> Sorry for the Inconvince the server are under maintain </h1><h4>Try again later...</h4>"

@app.route('/view1')
def view1():
    return '''<img src="/static/img/resume1.png" style="width: 100%">'''

@app.route('/view2')
def view2():
    return '''<img src="/static/img/resume2.png" style="width: 100%">'''

@app.route('/view3')
def view3():
    return '''<img src="/static/img/resume3.png" style="width: 100%">'''

app.run()
