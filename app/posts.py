from app import app, mysql, functions
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import MySQLdb


@app.route('/db/api/post/create', methods=['POST'])
def create_post():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'isApproved' not in content_json or 'user' not in content_json or 'date' not in content_json \
            or 'message' not in content_json or 'isSpam' not in content_json or 'isHighlighted' not in content_json \
            or 'thread' not in content_json or 'forum' not in content_json or 'isDeleted' not in content_json\
            or 'isEdited' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor()

    #try:
    cursor.execute(
        """INSERT INTO `posts` (`isApproved`, `user`, `date`, `message`, `isSpam`,`isHighlighted`, `thread`,
        `forum`,`isDeleted`, `isEdited`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
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
            content_json['isEdited']
        )
    )
    #except MySQLdb.Error:
    #    return jsonify({'code': 3, 'response': "Incorrect request: user is already exist"})
    post_id = cursor.lastrowid
    db.commit()
    content_json.update({'id': post_id})
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/post/details/', methods=['GET'])
def details_post():
    post_id = request.args.get('post', None)
    related = request.args.getlist('related', [])

    if post_id is ('' or None):
        return jsonify({'code': 2, 'response': "Incorrect request: some data missing"})
    post_id = int(post_id)

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

    if post is None:
        return jsonify({'code': 1, 'response': "Post not found"})

    post.update({'date': str(post['date'])})

    return jsonify({'code': 0, 'response': post})

@app.route('/db/api/post/remove', methods=['POST'])
def remove_post():
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
            """SELECT `isDeleted`
                FROM `posts`
                WHERE `id` = %s""",
            (int(content_json['post']),)
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    is_deleted = cursor.fetchone()
    if is_deleted is False:
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
    else:
        return jsonify({'code': 3, 'response':  "Incorrect request: post already delete"})

    return jsonify({'code': 0, 'response': {'post': content_json['post']}})

@app.route('/db/api/post/update', methods=['POST'])
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

@app.route('/db/api/post/vote', methods=['POST'])
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

@app.route('/db/api/post/restore', methods=['POST'])
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
            """SELECT `isDeleted`
                FROM `posts`
                WHERE `id` = %s""",
            (int(content_json['post']),)
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    is_deleted = cursor.fetchone()
    if is_deleted is True:
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
    else:
        return jsonify({'code': 3, 'response':  "Incorrect request: post exist"})

    return jsonify({'code': 0, 'response': {'post': content_json['post']}})


@app.route('/db/api/post/list/', methods=['GET'])
def list_posts():
    forum = request.args.get('forum', " ")
    thread = request.args.get('thread', " ")
    since = request.args.get('since', " ")
    limit = request.args.get('limit', None)
    order = request.args.get('order', 'DESC')

    if thread is None and forum is None:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    if thread is not None:
        thread_or_forum = " `thread` "
    else:
        thread_or_forum = " `forum` "

    if since is " ":
        since_str = " "
    else:
        since_str = " AND `date` >=  "

    if limit is None:
        limit = " "
    else:
        limit = ' LIMIT ' + limit

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:

        cursor.execute(
           """SELECT `id`, `message`, `forum`, `user`, `thread`, `likes`, `dislikes`, `points`, `isDeleted`,
`isSpam`, `isEdited`, `isApproved`, `isHighlighted`, `date`, `parent`
            FROM `posts`
            WHERE %s = %s %s """ + since_str + "%s" +
           " ORDER BY `date` " + order + limit + " ;",
            (
                thread_or_forum,
                thread,
                forum,
                since,)

            )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    posts = [i for i in cursor.fetchall()]
    for post in posts:
        post.update({'date': str(post['date'])})

    return jsonify({'code': 0, 'response': posts})
