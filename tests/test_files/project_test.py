from __future__ import absolute_import

from GitHubProjectManager.core.project.project import Project


def test_project():
    project = Project({"columns": {
        "nodes": [
            {
                "name": "Queue",
                "id": "1234",
                "cards": {
                      "pageInfo": {
                          "hasNextPage": True,
                          "endCursor": "MQ"
                      },
                    "edges": [
                          {
                              "cursor": "MQ",
                              "node": {
                                  "note": None,
                                  "state": "CONTENT_ONLY",
                                  "id": "3434=",
                                  "content": {
                                      "id": "1234=",
                                      "number": 1,
                                      "title": "issue 1",
                                      "labels": {
                                          "edges": [
                                              {
                                                  "node": {
                                                      "name": "High"
                                                  }
                                              },
                                              {
                                                  "node": {
                                                      "name": "bug"
                                                  }
                                              }
                                          ]
                                      },
                                      "assignees": {
                                          "edges": []
                                      }
                                  }
                              }
                          }
                      ]
                }
            },
            {
                "name": "Review in progress",
                "id": "5656",
                "cards": {
                      "pageInfo": {
                          "hasNextPage": True,
                          "endCursor": "MQ"
                      },
                    "edges": [
                          {
                              "cursor": "MQ",
                              "node": {
                                  "note": None,
                                  "state": "CONTENT_ONLY",
                                  "id": "56565=",
                                  "content": {
                                      "id": "5656=",
                                      "number": 17534,
                                      "title": "issue 2",
                                      "labels": {
                                          "edges": [
                                              {
                                                  "node": {
                                                      "name": "Medium"
                                                  }
                                              },
                                              {
                                                  "node": {
                                                      "name": "bug"
                                                  }
                                              }
                                          ]
                                      },
                                      "assignees": {
                                          "edges": [
                                              {
                                                  "node": {
                                                      "id": "234",
                                                      "name": "Rony Rony"
                                                  }
                                              }
                                          ]
                                      }
                                  }
                              }
                          }
                      ]
                }
            }
        ]
    }})

    assert len(project.all_issues) == 2
    assert len(project.columns.keys()) == 2
    assert project.done_column_name == 'Done'

    assert project.columns['Queue'].name == 'Queue'
    assert project.columns['Queue'].cards[0].issue_title == 'issue 1'

    assert project.columns['Review in progress'].name == 'Review in progress'
    assert project.columns['Review in progress'].cards[0].issue_title == 'issue 2'
