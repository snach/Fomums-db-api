from  app import app, mysql
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from flask import json
import ujson



@app.route('/db/api/user/create', methods=['POST'])
def create_user():
    parse_json = request.json
    print parse_json
    if parse_json['isAnonymous'] is None:
        parse_json['isAnonymous'] = False
    db = mysql.get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO `users` (`email`, `username`, `name`, `about`, `isAnonymous`)
VALUES (%s, %s, %s, %s, %s);""",
        (parse_json['email'], parse_json['username'], parse_json['name'], parse_json['about'], parse_json['isAnonymous']))
    user_id = cursor.lastrowid
    db.commit()
    parse_json.update({'id': user_id})
    return jsonify({'code': 0, 'response': parse_json})
