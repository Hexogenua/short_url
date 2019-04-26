from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
from flask_sqlalchemy import SQLAlchemy
import string
import sqlite3

from urllib.parse import urlparse

str_encode = str

from string import ascii_lowercase, ascii_uppercase

import base64

app = Flask(__name__)
host = 'http://localhost:5000/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)


class WEB_URL(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    URL = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "WEB_URL({})".format(self.URL)


def toBase62(num, b=62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + ascii_lowercase + ascii_uppercase
    r = num % b
    res = base[r]
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res


def toBase10(num, b=62):
    base = string.digits + ascii_lowercase + ascii_uppercase
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url'))

        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url

        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute('INSERT INTO WEB_URL (URL) VALUES (?)',[base64.urlsafe_b64encode(url.encode("utf-8"))])
            ##res = cursor.execute('INSERT INTO WEB_URL (URL) VALUES (?)',[base64.urlsafe_b64encode(url.encode("utf-8"))])
            encoded_string = toBase62(res.lastrowid)
        return render_template('home.html', short_url=host + encoded_string)
    return render_template('home.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded = toBase10(short_url)
    url = host  # fallback if no URL is found
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [decoded])

        try:
            short = res.fetchone()
            url = (base64.urlsafe_b64decode(short[0])).decode()
        except Exception as e:
            print (e) 

    return redirect(url)

if __name__ == '__main__':
    app.run()


