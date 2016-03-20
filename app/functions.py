def list_following(cursor, email):
    cursor.execute(
        """SELECT `followee`
        FROM `followers`
        WHERE `follower` = %s""",
        (email,)
    )
    z = cursor.fetchall()
    following = [i['followee'] for i in z]
    return following


def list_followers(cursor, email):
    cursor.execute\
        (
            """SELECT `follower`
            FROM `followers`
            WHERE `followee` = %s""",
            (email,)
        )
    z = cursor.fetchall()
    followers = [i['follower'] for i in z]
    return followers


def user_details(cursor, email):

    cursor.execute\
        (
            """SELECT *
            FROM `users`
            WHERE `email` = %s;""",
            (email,)
        )
    user = cursor.fetchone()

    if user is None:
        return None

    following = list_following(cursor, user['email'])
    followers = list_followers(cursor, user['email'])

    cursor.execute\
        (
            """SELECT `thread`
            FROM `subscriptions`
            WHERE `user` = %s;""",
            (email,)
        )
    threads = [i['thread'] for i in cursor.fetchall()]

    user.update({'following': following, 'followers': followers, 'subscriptions': threads})
    return user


def forum_details(cursor, short_name):
    cursor.execute\
        (
            """SELECT *
            FROM `forums`
            WHERE `short_name` = %s;""",
            (short_name,)
        )
    forum = cursor.fetchone()
    return forum


def thread_details(cursor, thread_id):
    cursor.execute\
        (
            """SELECT *
            FROM `threads`
            WHERE `id` = %s;""",
            (thread_id,)
        )
    thread = cursor.fetchone()

    if thread is None:
        return None

    thread.update({'date': str(thread['date'])})
    return thread


def post_details(cursor, post_id):
    cursor.execute\
        (
            """SELECT `id`, `message`, `forum`, `user`, `thread`, `likes`, `dislikes`, `points`, `isDeleted`,
    `isSpam`, `isEdited`, `isApproved`, `isHighlighted`, `date`, `parent`
            FROM `posts`
            WHERE `id` = %s;""",
            (post_id,)
        )
    post = cursor.fetchone()

    if post is None:
        return None

    post.update({'date': str(post['date'])})
    return post
