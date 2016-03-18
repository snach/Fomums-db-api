from app import app, mysql
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import MySQLdb



@app.route('/db/api/user/create', methods=['POST'])
def create_user():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if content_json.setdefault('isAnonymous'):
        content_json['name'] = ''
        content_json['username'] = ''
        content_json['about'] = ''
    else:
        if 'username' not in content_json or 'about' not in content_json or 'name' not in content_json \
                or 'email' not in content_json or 'isAnonymous' not in content_json:
            return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO `users` (`email`, `username`, `name`, `about`, `isAnonymous`)
             VALUES (%s, %s, %s, %s, %s);""",
            (
                content_json['email'],
                content_json['username'],
                content_json['name'],
                content_json['about'],
                content_json['isAnonymous'])
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request: user is already exist"})
    user_id = cursor.lastrowid
    db.commit()
    content_json.update({'id': user_id})
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/user/follow', methods=['POST'])
def create_follow():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})

