
from flask import Flask
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

con = sqlite3.connect("db.sqlite", check_same_thread=False)
cur = con.cursor()

from application import routes