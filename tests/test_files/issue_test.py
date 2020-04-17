from src.issue import Issue
from src.project_manager import ProjectManager


def test_issue_params():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug"]
    assignee = "ronykoz"

    issue = Issue({
            "comments": {
                "nodes": [
                    {
                        "author": {
                            "login": "ronykoz"
                        },
                        "body": "comment 1",
                        "createdAt": "2019-03-19T12:24:27Z"
                    },
                    {
                        "author": {
                            "login": "ronykoz"
                        },
                        "body": "second comment",
                        "createdAt": "2019-03-19T12:27:53Z"
                    },
                    {
                        "author": {
                            "login": "ronykoz"
                        },
                        "body": "third comment",
                        "createdAt": "2019-03-19T12:52:08Z"
                    }
                ]
            },
            "timelineItems": {
                "__typename": "IssueTimelineItemsConnection",
                "nodes": [
                    {
                        "__typename": "LabeledEvent",
                        "label": {
                            "name": labels[0]
                        },
                        "createdAt": "2019-03-15T12:40:22Z"
                    },
                    {
                        "__typename": "LabeledEvent",
                        "label": {
                            "name": labels[1]
                        },
                        "createdAt": "2019-03-17T13:59:27Z"
                    },
                    {
                        "__typename": "LabeledEvent",
                        "label": {
                            "name": labels[2]
                        },
                        "createdAt": "2019-04-08T10:48:02Z"
                    }
                ]
            },
            "title": title,
            "id": issue_id,
            "number": 1,
            "milestone": None,
            "labels": {
                "edges": [
                    {
                        "node": {
                            "name": labels[0]
                        }
                    },
                    {
                        "node": {
                            "name": labels[1]
                        }
                    },
                    {
                        "node": {
                            "name": labels[2]
                        }
                    }
                ]
            },
            "assignees": {
                "edges": [
                    {
                        "node": {
                            "login": assignee
                        }
                    }
                ]
            }
    }, ProjectManager.DEFAULT_PRIORITY_LIST)

    assert issue.id == issue_id
    assert issue.title == title
    assert issue.number == 1
    assert sorted(issue.labels) == sorted(labels)
    assert issue.priority_rank == 1
    assert issue.milestone is None
    for comment in issue.last_comments:
        assert 'ronykoz' in comment.to_readable()
        assert 'comment' in comment.to_readable()

    assert issue.pull_request is None
