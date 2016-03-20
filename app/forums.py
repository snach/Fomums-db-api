from app import app, mysql, functions
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

@app.route('/db/api/forum/details/', methods=['GET'])
def forum_detail():
    short_name = request.args.get('forum', None)
    related = request.args.get('related', [])

    if short_name is ('' or None):
        return jsonify({'code': 2, 'response': "Incorrect request: some data missing"})
    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute("""SELECT * FROM `forums` WHERE `short_name` = %s;""", (short_name,))
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    forum = cursor.fetchone()

    if related == 'user':
        user = functions.user_details(cursor, forum['user'])
        forum.update({'user': user})

    if forum is None:
        return jsonify({'code': 1, 'response': "Post not found"})

    return jsonify({'code': 0, 'response': forum})
