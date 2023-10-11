
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello to Lucanet Customer Success ChatBot !"

@app.route("/chat")
def chat():
	request.args.get('prompt')
    return promt