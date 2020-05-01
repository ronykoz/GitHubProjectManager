from __future__ import absolute_import

from GitHubProjectManager.core.issue.pull_request import PullRequest


def test_pull_request():
    assignee = "ronykoz"

    pull_request = PullRequest({
        "willCloseTarget": True,
        "source": {
            "__typename": "PullRequest",
            "state": "OPEN",
            "assignees": {
                "nodes": [
                    {
                        "login": assignee
                    }
                ],
            },
            "labels": {
                "nodes": [
                    {
                        "name": "label"
                    }
                ],
            },
            "reviewRequests": {
                "totalCount": 0
            },
            "reviews": {
                "totalCount": 1
            },
            "number": 1,
            "reviewDecision": "REVIEW_REQUIRED"
        },
        "__typename": "CrossReferencedEvent"
    })

    assert pull_request.number == 1
    assert pull_request.assignees == [assignee]
    assert pull_request.review_requested is True
    assert pull_request.review_completed is False
    assert "label" in pull_request.labels

    pull_request = PullRequest({
        "willCloseTarget": True,
        "source": {
            "__typename": "PullRequest",
            "state": "OPEN",
            "assignees": {
                "nodes": [
                    {
                        "login": assignee
                    }
                ],
            },
            "labels": {
                "nodes": [
                    {
                        "name": "label"
                    }
                ],
            },
            "reviewRequests": {
                "totalCount": 0
            },
            "reviews": {
                "totalCount": 0
            },
            "number": 1,
            "reviewDecision": "APPROVED"
        },
        "__typename": "CrossReferencedEvent"
    })

    assert pull_request.number == 1
    assert pull_request.assignees == [assignee]
    assert pull_request.review_requested is False
    assert pull_request.review_completed is True
