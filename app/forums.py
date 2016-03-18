from app import app, mysql
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import MySQLdb



@app.route('/db/api/forum/create', methods=['POST'])
def create_forum():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'name' not in content_json or 'short_name' not in content_json or 'user' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})
    db = mysql.get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO `forums` (`name`, `short_name`, `user`)
    VALUES (%s, %s, %s);""",
            (
                content_json['name'],
                content_json['short_name'],
                content_json['user']
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request: name and short_name must be unique"})
    forum_id = cursor.lastrowid
    db.commit()
    content_json.update({'id': forum_id})
    return jsonify({'code': 0, 'response': content_json})
