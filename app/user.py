from app import app, mysql, functions
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
                content_json['isAnonymous']
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request: user is already exist"})
    user_id = cursor.lastrowid
    db.commit()
    content_json.update({'id': user_id})
    return jsonify({'code': 0, 'response': content_json})

@app.route('/db/api/user/details/', methods=['GET'])
def details_user():
    user_email = request.args.get('user', None)
    if user_email is ('' or None):
        return jsonify({'code': 2, 'response': "Incorrect request: some data missing"})
    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    user = functions.user_details(cursor, user_email)

    if user is None:
        return jsonify({'code': 1, 'response': 'User not found '})
    return jsonify({'code': 0, 'response': user})

@app.route('/db/api/user/follow', methods=['POST'])
def create_follow():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'follower' not in content_json or 'followee' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})
    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(
            """INSERT INTO `followers` (`follower`, `followee`)
             VALUES (%s, %s);""",
            (
                content_json['follower'],
                content_json['followee']
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    db.commit()
    user = functions.user_details(cursor, content_json['follower'])
    return jsonify({'code': 0, 'response': user})

@app.route('/db/api/user/updateProfile', methods=['POST'])
def update_user():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'user' not in content_json or 'about' not in content_json or 'name' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(
            """UPDATE `users` SET `about` = %s, `name` = %s WHERE `email` = %s;""",
            (
                content_json['about'],
                content_json['name'],
                content_json['user']
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request: user is already exist"})
    db.commit()
    user = functions.user_details(cursor, content_json['user'])
    return jsonify({'code': 0, 'response': user})

@app.route('/db/api/user/unfollow', methods=['POST'])
def delete_follow():
    try:
        content_json = request.json
    #    print content_json
    except BadRequest:
        return jsonify({'code': 2, 'response': "Invalid request(syntax)"})
    if 'follower' not in content_json or 'followee' not in content_json:
        return jsonify({'code': 3, 'response':  "Incorrect request: some data missing"})

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(
            """DELETE FROM `followers`
                WHERE `follower` = %s and `followee` = %s;""",
            (
                content_json['follower'],
                content_json['followee']
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    db.commit()
    user = functions.user_details(cursor, content_json['follower'])
    return jsonify({'code': 0, 'response': user})

@app.route('/db/api/user/listFollowers/', methods=['GET'])
def list_followers():
    user_email = request.args.get('user', None)
    order = request.args.get('order', 'DESC')
    limit = request.args.get('limit', None)
    since_id = request.args.get('since_id', '1')

    if user_email is None:
        return jsonify({'code': 1, 'response': "User not found "})

    if limit is None:
        limit = " "
    else:
        limit = 'LIMIT ' + limit

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(
            """SELECT `about`, `email`, `id`, `isAnonymous`, `name`, `username` FROM `followers` AS `f`
                JOIN `users` ON `users`.`email` = `f`.`follower`
                WHERE `f`.`followee` = %s AND `users`.`id` >= %s
                ORDER BY `name` """ + order + limit + " ;",
            (
                user_email,
                int(since_id)
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    users = [i for i in cursor.fetchall()]

    for user in users:
        following = functions.list_following(cursor, user['email'])
        followers = functions.list_followers(cursor, user['email'])

        cursor.execute(
            """SELECT `thread`
                FROM `subscriptions`
                WHERE `user` = %s;""",
            (
                user['email'],
            )
        )
        threads = [i['thread'] for i in cursor.fetchall()]

        user.update({'following': following, 'followers': followers, 'subscriptions': threads})

    return jsonify({'code': 0, 'response': users})

@app.route('/db/api/user/listFollowing/', methods=['GET'])
def list_following():
    user_email = request.args.get('user', None)
    order = request.args.get('order', 'DESC')
    limit = request.args.get('limit', None)
    since_id = request.args.get('since_id', '1')

    if user_email is None:
        return jsonify({'code': 1, 'response': "User not found "})

    if limit is None:
        limit = " "
    else:
        limit = 'LIMIT ' + limit

    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(
            """SELECT `about`, `email`, `id`, `isAnonymous`, `name`, `username` FROM `followers` AS `f`
                JOIN `users` ON `users`.`email` = `f`.`followee`
                WHERE `f`.`follower` = %s AND `users`.`id` >= %s
                ORDER BY `name` """ + order + limit + " ;",
            (
                user_email,
                int(since_id)
            )
        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})
    users = [i for i in cursor.fetchall()]
    for user in users:
        following = functions.list_following(cursor, user['email'])
        followers = functions.list_followers(cursor, user['email'])

        cursor.execute("""SELECT `thread` FROM `subscriptions` WHERE `user` = %s;""", (user['email'],))
        threads = [i['thread'] for i in cursor.fetchall()]

        user.update({'following': following, 'followers': followers, 'subscriptions': threads})
    return jsonify({'code': 0, 'response': users})


@app.route('/db/api/user/listPosts/', methods=['GET'])
def list_posts():
    user_email = request.args.get('user', None)

    since = request.args.get('since', " ")
    limit = request.args.get('limit', None)
    order = request.args.get('order', 'DESC')

    if user_email is None:
        return jsonify({'code': 1, 'response': "User not found "})

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
            WHERE `user` = %s """ + since_str + "%s" +
           " ORDER BY `date` " + order + limit + " ;",
            (user_email, since,)

        )
    except MySQLdb.Error:
        return jsonify({'code': 3, 'response': "Incorrect request"})

    posts = [i for i in cursor.fetchall()]

    for post in posts:
        post.update({'date': str(post['date'])})

    return jsonify({'code': 0, 'response': posts})


