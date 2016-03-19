def list_following(cursor, email):
    cursor.execute("""SELECT `followee` FROM `followers` WHERE `follower` = %s""", (email,))
    z = cursor.fetchall()
    following = [i['followee'] for i in z]
    return following


def list_followers(cursor, email):
    cursor.execute("""SELECT `follower` FROM `followers` WHERE `followee` = %s""", (email,))
    z = cursor.fetchall()
    followers = [i['follower'] for i in z]
    return followers


def user_details(cursor, email):
    cursor.execute("""SELECT * FROM `users` WHERE `email` = %s;""", (email,))
    user = cursor.fetchone()

    if user is None:
        return None

    following = list_following(cursor, user['email'])
    followers = list_followers(cursor, user['email'])

    cursor.execute("""SELECT `thread` FROM `subscriptions` WHERE `user` = %s;""", (email,))
    threads = [i['thread'] for i in cursor.fetchall()]

    user.update({'following': following, 'followers': followers, 'subscriptions': threads})
    return user