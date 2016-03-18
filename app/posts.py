from app import app, mysql
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
    if post_id is ('' or None):
        return jsonify({'code': 2, 'response': "Incorrect request: some data missing"})
    post_id = int(post_id)
    db = mysql.get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""SELECT `id`, `message`, `forum`, `user`, `thread`, `likes`, `dislikes`, `points`, `isDeleted`,
`isSpam`, `isEdited`, `isApproved`, `isHighlighted`, `date`, `parent` FROM `posts` WHERE `id` = %s;""", (post_id,))
    post = cursor.fetchone()
    print post
    if post is None:
        return jsonify({'code': 1, 'response': "Post not found"})
    post.update({'date': str(post['date'])})
    return jsonify({'code': 0, 'response': post})

