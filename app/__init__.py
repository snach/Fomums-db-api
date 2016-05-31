from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'rootPassword'
app.config['MYSQL_DATABASE_DB'] = 'db_Forums'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_CHARSET'] = 'utf-8'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False


mysql.init_app(app)

from views import *
from app import user
from app import forums
from app import threads
from app import posts

