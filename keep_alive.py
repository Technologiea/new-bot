from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return "Alive"

def run():
    app.run(host='0.0.0.0', port=8081)  # Use port 8081 to avoid conflict with main.py

def keep_alive():
    t = Thread(target=run)
    t.start()
