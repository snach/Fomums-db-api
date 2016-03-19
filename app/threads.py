from app import app, mysql
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import MySQLdb



@app.route('/db/api/thread/create', methods=['POST'])
def create_thread():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'forum' not in content_json or 'title' not in content_json or 'isClosed' not in content_json \
            or 'user' not in content_json or 'date' not in content_json or 'message' not in content_json \
            or 'slug' not in content_json or 'isDeleted' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            """INSERT INTO `threads` (`forum`, `title`, `isClosed`, `user`, `date`,`message`, `slug`, `isDeleted`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
            (
                content_json['forum'],
                content_json['title'],
                content_json['isClosed'],
                content_json['user'],
                content_json['date'],
                content_json['message'],
                content_json['slug'],
                content_json['isDeleted']
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request: user is already exist"})
    thread_id = cursor.lastrowid
    db.commit()
    content_json.update({'id': thread_id})
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/thread/subscribe', methods=['POST'])
def subscribe():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'user' not in content_json or 'thread' not in content_json :
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})
    db = mysql.get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO `subscriptions` (`user`, `thread`)
    VALUES (%s, %s);""",
            (
                content_json['user'],
                content_json['thread'],
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    db.commit()
    return jsonify({'code': 0, 'response': content_json})
