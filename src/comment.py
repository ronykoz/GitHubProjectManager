class Comment(object):
    def __init__(self, comment_object):
        self.creator = comment_object['author']['login']
        self.body = comment_object['body']
        self.created_at = comment_object['createdAt']

    def to_readable(self):
        return f'{self.created_at} --- {self.creator} wrote:\n{self.body}'
