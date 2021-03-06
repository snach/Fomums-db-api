from app import app, mysql
from flask import jsonify


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/db/api/clear/', methods=['POST'])
def clear():
    db = mysql.get_db()
    cursor = db.cursor()

    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    cursor.execute('TRUNCATE TABLE users')
    cursor.execute('TRUNCATE TABLE threads')
    cursor.execute('TRUNCATE TABLE posts')
    cursor.execute('TRUNCATE TABLE forums')
    cursor.execute('TRUNCATE TABLE followers')
    cursor.execute('TRUNCATE TABLE subscriptions')
    cursor.execute('SET FOREIGN_KEY_CHECKS=1')

    db.commit()
    return jsonify({'code': 0, 'response': 'OK'})

@app.route('/db/api/status/', methods=['GET'])
def status():
    tables = ['users', 'threads', 'forums', 'posts']
    response = {}
    db = mysql.get_db()
    cursor = db.cursor()
    for table in tables:
        cursor.execute('SELECT COUNT(1) FROM %s' % table)
        db.commit()
        response[table] = cursor.fetchone()[0]
    #db.close()
    return jsonify({'code': 0, 'response': response})
