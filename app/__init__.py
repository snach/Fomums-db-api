from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'rootPassword'
app.config['MYSQL_DATABASE_DB'] = 'db_Forums'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

from app import views
from app import user
