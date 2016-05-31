from app import app, mysql, functions
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import MySQLdb
from numconv import int2str


@app.route('/db/api/post/create/', methods=['POST'])
def create_post():
    try:
        content_json = request.json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'isApproved' not in content_json or 'user' not in content_json or 'date' not in content_json \
            or 'message' not in content_json or 'isSpam' not in content_json or 'isHighlighted' not in content_json \
            or 'thread' not in content_json or 'forum' not in content_json or 'isDeleted' not in content_json\
            or 'isEdited' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor()

    if content_json['parent'] is None:
        isRoot = True
        path = ''
    else:
        isRoot = False
        cursor.execute("""SELECT `path` FROM `posts` WHERE `id` = %s""", (content_json['parent'],))
        path = cursor.fetchone()[0]

    try:
        cursor.execute(
            """INSERT INTO `posts` (`isApproved`, `user`, `date`, `message`, `isSpam`,`isHighlighted`, `thread`,
            `forum`,`isDeleted`, `isEdited`,`parent`,`isRoot`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            (
                content_json['isApproved'],
                content_json['user'],
                content_json['date'],
                content_json['message'],
                content_json['isSpam'],
                content_json['isHighlighted'],
                content_json['thread'],
                content_json['forum'],
                content_json['isDeleted'],
                content_json['isEdited'],
                content_json['parent'],
                isRoot
            )
        )
        post_id = cursor.lastrowid

        base36 = int2str(int(post_id), radix=36)
        path += str(len(base36)) + base36

        cursor.execute("""UPDATE `posts` SET path = %s WHERE `id` = %s""", (path, post_id))
        cursor.execute("""UPDATE `threads` SET `posts` = `posts` + 1 WHERE `id` = %s;""", (content_json['thread'],))

    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request: post is already exist"})

    db.commit()
    content_json.update({'id': post_id})
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/post/details/', methods=['GET'])
def details_post():
    post_id = request.args.get('post', None)
    related = request.args.getlist('related')

    if post_id is None:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    post_id = int(post_id)

    if post_id < 1:
        return jsonify({'code': 1, 'response':  "Incorrect request: post don\'t found"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    post = functions.post_details(cursor, post_id)

    if 'user' in related:
        user = functions.user_details(cursor, post['user'])
        post.update({'user': user})

    if 'forum' in related:
        forum = functions.forum_details(cursor, post['forum'])
        post.update({'forum': forum})

    if 'thread' in related:
        thread = functions.thread_details(cursor, post['thread'])
        post.update({'thread': thread})

    return jsonify({'code': 0, 'response': post})

@app.route('/db/api/post/remove/', methods=['POST'])
def remove_post():
    try:
        content_json = request.json
        print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'post' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(
            """UPDATE `threads` SET `posts` = `posts` - 1
            WHERE `id` = (
                            SELECT `thread`
                            FROM `posts`
                            WHERE `id` = %s
                            );""",
            (int(content_json['post']),)
        )
        cursor.execute("""UPDATE `posts` SET `isDeleted` = TRUE WHERE `id` = %s;""", (content_json['post'],))

        db.commit()

    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    return jsonify({'code': 0, 'response': {'post': content_json['post']}})

@app.route('/db/api/post/update/', methods=['POST'])
def update_post():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'post' not in content_json or 'message' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(
            """UPDATE `posts` SET `message` = %s
            WHERE `id` = %s;""",
            (
               content_json['message'],
               int(content_json['post']),
            )
        )

        db.commit()

    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    post = functions.post_details(cursor, int(content_json['post']))

    return jsonify({'code': 0, 'response': post})

@app.route('/db/api/post/vote/', methods=['POST'])
def vote_post():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'post' not in content_json or 'vote' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if content_json['vote'] != 1 and content_json['vote'] != -1:
        return jsonify({'code': 3, 'response':  "Incorrect request: vote is wrong"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        if content_json['vote'] == 1:
            cursor.execute(
                """UPDATE `posts` SET `likes` = `likes` + 1, `points` = `points` + 1
                WHERE `id` = %s;""",
                (int(content_json['post']),))
        else:
            cursor.execute(
                """UPDATE `posts` SET `dislikes` = `dislikes` + 1, `points` = `points` - 1
                WHERE `id` = %s;""",
                (int(content_json['post']),))
        db.commit()

    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    post = functions.post_details(cursor, int(content_json['post']))

    return jsonify({'code': 0, 'response': post})

@app.route('/db/api/post/restore/', methods=['POST'])
def restore_post():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'post' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(
            """UPDATE `threads` SET `posts` = `posts` + 1
            WHERE `id` = (
                            SELECT `thread`
                            FROM `posts`
                            WHERE `id` = %s
                            );""",
            (int(content_json['post']),)
        )
        cursor.execute("""UPDATE `posts` SET `isDeleted` = FALSE WHERE `id` = %s;""", (content_json['post'],))

        db.commit()

    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    return jsonify({'code': 0, 'response': {'post': content_json['post']}})


@app.route('/db/api/post/list/', methods=['GET'])
def list_posts():
    forum = request.args.get('forum', None)
    thread = request.args.get('thread', None)
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order', 'desc')

    if thread is None and forum is None:

        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if forum is not None:
        query = """SELECT * FROM `posts` WHERE `forum` = %s """
        query_params = (forum,)
    else:
        query = """SELECT * FROM `posts` WHERE `thread` = %s """
        query_params = (thread,)

    if since is not None:
        query += "AND `date` >= %s "
        query_params += (since,)

    query += "ORDER BY `date` " + order + " "

    if limit is not None:
        query += "LIMIT %s;"
        query_params += (int(limit),)

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, query_params)

    posts = [i for i in cursor.fetchall()]

    for post in posts:
        post.update({'date': str(post['date'])})

    return jsonify({'code': 0, 'response': posts})


