from __future__ import absolute_import

from GitHubProjectManager.core.issue.comment import Comment


def test_comment_to_readable():
    created_at = "2019-03-19T12:27:53Z"
    body = "this is the comment test"
    login = 'test'
    comment = Comment(
        {
            "author": {
                "login": login
            },
            "body": body,
            "createdAt": created_at
        }
    )
    assert comment.to_readable() == f'{created_at} --- {login} wrote:\n{body}'
