from app import app, mysql, functions
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import MySQLdb



@app.route('/db/api/thread/create/', methods=['POST'])
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
    thread_id = 0
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

        thread_id = cursor.lastrowid
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request: user is already exist"})
    db.commit()
    content_json.update({'id': thread_id})
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/thread/subscribe/', methods=['POST'])
def subscribe():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'user' not in content_json or 'thread' not in content_json:
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

@app.route('/db/api/thread/details/', methods=['GET'])
def thread_detail():
    thread_id = request.args.get('thread', None)
    related = request.args.getlist('related')
    thread_id = int(thread_id)
    if thread_id is ('' or None) and thread_id <= 0:
        return jsonify({'code': 2, 'response': "Incorrect request: some data missing"})
    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    thread = functions.thread_details(cursor, thread_id)

    if thread is None:
        return jsonify({'code': 1, 'response': "Post not found"})
    if 'thread' in related:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    if 'user' in related:
        user = functions.user_details(cursor, thread['user'])
        thread.update({'user': user})

    if 'forum' in related:
        forum = functions.forum_details(cursor, thread['forum'])
        thread.update({'forum': forum})

    return jsonify({'code': 0, 'response': thread})

@app.route('/db/api/thread/update/', methods=['POST'])
def update_thread():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'message' not in content_json or 'slug' not in content_json or 'thread' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(
            """UPDATE `threads` SET `message` = %s, `slug` = %s
            WHERE `id` = %s;""",
            (
                content_json['message'],
                content_json['slug'],
                int(content_json['thread'])
            )
        )
        db.commit()
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    thread = functions.thread_details(cursor, int(content_json['thread']))

    return jsonify({'code': 0, 'response': {'thread': thread}})

@app.route('/db/api/thread/vote/', methods=['POST'])
def vote_thread():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'thread' not in content_json or 'vote' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if content_json['vote'] != 1 and content_json['vote'] != -1:
        return jsonify({'code': 3, 'response':  "Incorrect request: vote is wrong"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        if content_json['vote'] == 1:
            cursor.execute(
                """UPDATE `threads` SET `likes` = `likes` + 1, `points` = `points` + 1
                WHERE `id` = %s;""",
                (int(content_json['thread']),))
        else:
            cursor.execute(
                """UPDATE `threads` SET `dislikes` = `dislikes` + 1, `points` = `points` - 1
                WHERE `id` = %s;""",
                (int(content_json['thread']),))
        db.commit()

    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    thread = functions.thread_details(cursor, int(content_json['thread']))

    return jsonify({'code': 0, 'response': thread})

@app.route('/db/api/thread/unsubscribe/', methods=['POST'])
def unsubscribe():
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
            """DELETE FROM`subscriptions`
                WHERE `user` = %s AND `thread` = %s ;""",
            (
                content_json['user'],
                int(content_json['thread']),
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    db.commit()
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/thread/close/', methods=['POST'])
def close_thread():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'thread' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            """UPDATE `threads` SET `isClosed` = TRUE
            WHERE `id` = %s;""",
            (int(content_json['thread']),)
        )
    except MySQLdb.Error:
        db.rollback()

    db.commit()
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/thread/open/', methods=['POST'])
def open_thread():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'thread' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            """UPDATE `threads` SET `isClosed` = FALSE
            WHERE `id` = %s;""",
            (int(content_json['thread']),)
        )
    except MySQLdb.Error:
        db.rollback()

    db.commit()
    return jsonify({'code': 0, 'response': content_json})


@app.route('/db/api/thread/remove/', methods=['POST'])
def remove_thread():
    try:
        content_json = request.json
        print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'thread' not in content_json or int(content_json['thread']) <= 0:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(
            """SELECT `isDeleted`
                FROM `threads`
                WHERE `id` = %s""",
            (int(content_json['thread']),)
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    is_deleted = cursor.fetchone()

    if is_deleted['isDeleted'] is 0:
        try:

            cursor.execute("""UPDATE `threads` SET `isDeleted` = TRUE, `posts` = 0 WHERE `id` = %s;""",
                (content_json['thread'],))
            cursor.execute(
                """UPDATE `posts` SET `isDeleted` = TRUE WHERE `thread` = %s;""",
                (content_json['thread'],)
            )


            db.commit()

        except MySQLdb.Error:
            return jsonify({'code': 3, 'response': "Incorrect request"})
    else:
        return jsonify({'code': 3, 'response':  "Incorrect request: thread already delete"})

    return jsonify({'code': 0, 'response': {'thread': content_json['thread']}})


@app.route('/db/api/thread/restore/', methods=['POST'])
def restore_thread():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'thread' not in content_json or int(content_json['thread']) <= 0:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(
            """SELECT `isDeleted`
                FROM `threads`
                WHERE `id` = %s""",
            (int(content_json['thread']),)
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    is_deleted = cursor.fetchone()
    if is_deleted['isDeleted'] is 1:
        try:
            count = cursor.execute(
                """UPDATE `posts` SET `isDeleted` = FALSE
                WHERE `thread` = %s;""",
                (content_json['thread'],)
            )
            cursor.execute(
                """UPDATE `threads` SET `isDeleted` = FALSE, `posts` = %s
                WHERE `id` = %s;""",
                (count, content_json['thread'])
            )
            db.commit()

        except MySQLdb.Error:
            return jsonify({'code': 3, 'response': "Incorrect request"})
    else:
        return jsonify({'code': 3, 'response':  "Incorrect request: thread exist"})

    return jsonify({'code': 0, 'response': {'thread': content_json['thread']}})


@app.route('/db/api/thread/list/', methods=['GET'])
def list_threads_from_thread():
    forum = request.args.get('forum', None)
    user = request.args.get('user', None)
    since = request.args.get('since', None)
    limit = request.args.get('limit', None)
    order = request.args.get('order', 'DESC')

    if user is None and forum is None:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if user is not None:
        query = """SELECT * FROM `threads` WHERE `user` = %s """
        query_params = (user,)
    else:
        query = """SELECT * FROM `threads` WHERE `forum` = %s """
        query_params = (forum,)

    if since is not None:
        query += "AND `date` >= %s "
        query_params += (since,)

    query += "ORDER BY `date` " + order + " "

    if limit is not None:
        query += "LIMIT %s;"
        query_params += (int(limit),)

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(query,query_params)
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    threads = [i for i in cursor.fetchall()]
    for thread in threads:
        thread.update({'date': str(thread['date'])})

    return jsonify({'code': 0, 'response': threads})

@app.route('/db/api/thread/listPosts/', methods=['GET'])
def list_posts_from_threads():
    thread = request.args.get('thread', None)
    since = request.args.get('since', " ")
    limit = request.args.get('limit', None)
    order = request.args.get('order', 'desc')
    sort = request.args.get('sort', 'flat')
    print ("snach")
    if sort is "flat":
        if thread is None:
            return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

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

        try:
            cursor.execute(query, query_params)
        except MySQLdb.Error:
            return jsonify({'code': 3, 'response': "Incorrect request"})

        posts = [i for i in cursor.fetchall()]
        for post in posts:
            post.update({'date': str(post['date'])})

        return jsonify({'code': 0, 'response': posts})






