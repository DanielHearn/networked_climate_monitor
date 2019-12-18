from flask import Flask, render_template, redirect, jsonify, request
from random import *
from tinydb import TinyDB, Query
db = TinyDB('db.json')

app = Flask(__name__)


@app.route('/api/fruit', methods=["GET", "POST"])
def fruit():
    if request.method == "POST":
        db.insert({'type': 'peach', 'count': 3})
        return jsonify({'status': 'success'})
    return jsonify(db.all())


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
