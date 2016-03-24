from app import app, mysql, functions
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import MySQLdb



@app.route('/db/api/forum/create/', methods=['POST'])
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

@app.route('/db/api/forum/listUsers/', methods=['GET'])
def list_users():
    forum = request.args.get('forum', None)
    since_id = request.args.get('since_id', None)
    limit = request.args.get('limit', None)
    order = request.args.get('order', 'DESC')

    if forum is None:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if since_id is None:
        since_str = " "
    else:
        since_str = " AND `id` >=  " + since_id

    if limit is None:
        limit = " "
    else:
        limit = ' LIMIT ' + limit

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:

        cursor.execute(
            """SELECT * FROM `users`
            WHERE `email` IN (SELECT DISTINCT `user` FROM `posts` WHERE `forum` = %s)"""
            + since_str +
            " ORDER BY `name` " + order + limit + " ;",
            (
                forum,

            )

        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    resp = []
    users = [i for i in cursor.fetchall()]
    for user in users:
        user = functions.user_details(cursor, user['email'])
        resp.append(user)

    return jsonify({'code': 0, 'response': resp})

@app.route('/db/api/forum/listThreads/', methods=['GET'])
def list_threads():
    forum = request.args.get('forum', None)
    since = request.args.get('since', None)
    limit = request.args.get('limit', None)
    order = request.args.get('order', 'DESC')
    related = request.args.getlist('related', [])

    if forum is None:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if since is None:
        since_str = " "
    else:
        since_str = " AND `date` >=  " + since

    if limit is None:
        limit = " "
    else:
        limit = ' LIMIT ' + limit

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:

        cursor.execute(
            """SELECT * FROM `threads` WHERE `forum` = %s """ + since_str  +
            " ORDER BY `date` " + order + limit + " ;",
            (
                forum,
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    resp = []

    threads = [i for i in cursor.fetchall()]

    for thread in threads:
        if 'user' in related:
            user = functions.user_details(cursor, thread['user'])
            thread.update({'user': user})

        if 'forum' in related:
            forum = functions.forum_details(cursor, thread['forum'])
            thread.update({'forum': forum})

        thread.update({'date': str(thread['date'])})
        resp.append(thread)

    return jsonify({'code': 0, 'response': resp})

@app.route('/db/api/forum/listPosts/', methods=['GET'])
def list_posts():
    forum = request.args.get('forum', None)
    since = request.args.get('since', None)
    limit = request.args.get('limit', None)
    order = request.args.get('order', 'DESC')
    related = request.args.getlist('related', [])

    if forum is None:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if since is None:
        since_str = " "
    else:
        since_str = " AND `date` >=  " + since

    if limit is None:
        limit = " "
    else:
        limit = ' LIMIT ' + limit

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:

        cursor.execute(
            """SELECT `id`, `message`, `forum`, `user`, `thread`, `likes`, `dislikes`, `points`, `isDeleted`,
`isSpam`, `isEdited`, `isApproved`, `isHighlighted`, `date`, `parent` FROM `posts`
            FROM `posts` WHERE `forum` = %s """ + since_str +
            " ORDER BY `date` " + order + limit + " ;",
            (
                forum,

            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    posts = [i for i in cursor.fetchall()]
    resp = []
    for post in posts:
        if 'user' in related:
            user = functions.user_details(cursor, post['user'])
            post.update({'user': user})

        if 'forum' in related:
            forum = functions.forum_details(cursor, post['forum'])
            post.update({'forum': forum})

        if 'thread' in related:
            thread = functions.thread_details(cursor, post['thread'])
            post.update({'thread': thread})

        post.update({'date': str(post['date'])})
        resp.append(post)

    return jsonify({'code': 0, 'response': resp})
