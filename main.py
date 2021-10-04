import os

from flask import Flask, render_template


app = Flask(__name__, template_folder=os.path.dirname(__file__))


@app.route('/', methods=['GET'])
def handle_request():
    return (render_template(
        'index.html',
    ), 200)
