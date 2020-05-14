from __future__ import absolute_import

import os

import pytest
from GitHubProjectManager.common.constants import DEFAULT_PRIORITY_LIST
from GitHubProjectManager.core.issue.issue import Issue
from GitHubProjectManager.core.project.project import (IssueCard, Project, ProjectColumn, parse_project,
                                                       _extract_card_node_data)
from GitHubProjectManager.management.configuration import Configuration

MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


def test_project():
    project = Project(**parse_project({
        "name": "test",
        "columns": {
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
                                          "number": 15,
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
                                                          "login": "Rony Rony"
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
        }
    }, Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))))

    assert len(project.get_all_issue_ids()) == 2
    assert len(project.columns.keys()) == 2

    assert project.columns['Queue'].name == 'Queue'
    assert project.columns['Queue'].cards[0].issue_title == 'issue 1'

    assert project.columns['Review in progress'].name == 'Review in progress'
    assert project.columns['Review in progress'].cards[0].issue_title == 'issue 2'


def test_empty_config_for_issue_card():
    with pytest.raises(Exception) as raised_exception:
        IssueCard("test id")
        assert "You must provide configuration file loading new issue" in raised_exception


def test_set_issue_to_issue_card():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug"]
    assignee = "ronykoz"
    issue = Issue(
        id=issue_id,
        number=1,
        title=title,
        labels=labels,
        assignees=[assignee]
    )
    card = IssueCard("id", issue=issue)
    assert card.id == 'id'
    assert card.issue == issue


def test_project_empty_card():
    project = Project(
        name="test project",
        config=Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini')),
        columns={
            "Queue": ProjectColumn(id="id", name="Queue",
                                   cards=[IssueCard(id="sdf",
                                                    issue=Issue(id="sdf", title="title", number=1))]),
            "Review in progress": ProjectColumn(id="id", name="Review in progress",
                                                cards=[])
        }
    )

    assert project.name == "test project"
    assert len(project.get_all_issue_ids()) == 1
    assert len(project.columns.keys()) == 2

    assert project.columns['Queue'].name == 'Queue'

    assert project.columns['Review in progress'].name == 'Review in progress'


def test_add_card_to_column():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()

    config.priority_list = DEFAULT_PRIORITY_LIST
    column_object = ProjectColumn(id="id", name="Review in progress",
                                  cards=[
                                      IssueCard(id="sdf",
                                                issue=Issue(id="sdf", title="issue 2", number=2, labels=["Low"])),
                                      IssueCard(id="sdf2",
                                                issue=Issue(id="sdf2", title="issue 3", number=3, labels=["High"]))
                                  ])
    issue_to_inject = Issue(
        id="4",
        title="issue 4",
        number=4,
        labels=['Medium']
    )
    issue_to_inject.set_priority(DEFAULT_PRIORITY_LIST)

    class MockClient(object):
        def add_to_column(*args, **kwargs):
            return

        def move_to_specific_place_in_column(*args, **kwargs):
            return

    mock_client = MockClient()

    # Sorting
    column_object.sort_cards(mock_client, config)
    card_titles_in_column = [card.issue.title for card in column_object.cards]
    assert card_titles_in_column == ['issue 3', 'issue 2']

    # Adding in the middle
    column_object.add_card("id", issue_to_inject, mock_client)
    card_titles_in_column = [card.issue.title for card in column_object.cards]
    assert card_titles_in_column == ['issue 3', 'issue 4', 'issue 2']

    # Higher priority addition
    issue_to_inject2 = Issue(
        id="5",
        title="issue 5",
        number=5,
        labels=['Critical']
    )
    issue_to_inject2.set_priority(DEFAULT_PRIORITY_LIST)

    column_object.add_card("id", issue_to_inject2, mock_client)
    card_titles_in_column = [card.issue.title for card in column_object.cards]
    assert card_titles_in_column == ['issue 5', 'issue 3', 'issue 4', 'issue 2']

    # Lower priority addition
    issue_to_inject3 = Issue(
        id="6",
        title="issue 6",
        number=6
    )

    column_object.add_card("id", issue_to_inject3, mock_client)
    card_titles_in_column = [card.issue.title for card in column_object.cards]
    assert card_titles_in_column == ['issue 5', 'issue 3', 'issue 4', 'issue 2', "issue 6"]

    # Same priority different number
    issue_to_inject4 = Issue(
        id="7",
        title="issue 7",
        number=-1,
    )

    column_object.add_card("id", issue_to_inject4, mock_client)
    card_titles_in_column = [card.issue.title for card in column_object.cards]
    assert card_titles_in_column == ['issue 5', 'issue 3', 'issue 4', 'issue 2', "issue 7", "issue 6"]


def test_sort_column():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()

    class MockClient(object):
        def add_to_column(*args, **kwargs):
            return

        def move_to_specific_place_in_column(*args, **kwargs):
            return

    mock_client = MockClient()
    # Sorting
    config.priority_list = DEFAULT_PRIORITY_LIST
    column_object = ProjectColumn(
        id="id", name="Review in progress",
        cards=[
          IssueCard(id="sdf",
                    issue=Issue(id="sdf", title="issue 2", number=2, labels=["Low"])),
          IssueCard(id="sdf3",
                    issue=Issue(id="sdf", title="issue 4", number=4, labels=["Medium"])),
          IssueCard(id="sdf2",
                    issue=Issue(id="sdf2", title="issue 3", number=3, labels=["High"]))
              ])

    column_object.sort_cards(mock_client, config)
    card_titles_in_column = [card.issue.title for card in column_object.cards]

    assert card_titles_in_column == ['issue 3', "issue 4", 'issue 2']


def test_get_matching_column():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()

    issue_queue = Issue(
        id="1",
        title="issue 1",
        number=1
    )
    assert Project.get_matching_column(issue_queue, config) == 'Queue'

    issue_in_progress = Issue(
        id="1",
        title="issue 1",
        number=1
    )
    issue_in_progress.add_assignee("Rony")
    assert Project.get_matching_column(issue_in_progress, config) == ''
    issue_in_progress.add_label("Testing")
    assert Project.get_matching_column(issue_in_progress, config) == 'In progress'

    issue_review_in_progress = Issue(
        id="1",
        title="issue 1",
        number=1
    )
    issue_review_in_progress.add_assignee("Rony")

    class MockPullRequest(object):
        review_requested = True
        review_completed = False

    issue_review_in_progress.pull_request = MockPullRequest()

    assert Project.get_matching_column(issue_review_in_progress, config) == 'Review in progress'

    issue_docs = Issue(
        id="1",
        title="issue 1",
        number=1
    )
    issue_docs.add_assignee("Rony")

    class MockPullRequest2(object):
        review_requested = True
        review_completed = True
        assignees = "ronykoz"

    issue_docs.pull_request = MockPullRequest2()

    assert Project.get_matching_column(issue_docs, config) == 'Waiting for Docs'

    class MockPullRequest3(object):
        review_requested = True
        review_completed = True
        assignees = "someone"

    issue_docs.pull_request = MockPullRequest3()

    assert Project.get_matching_column(issue_docs, config) == 'Review in progress'

    # faulty field from issues
    config.column_to_rules["Waiting for Docs"] = {
        "issue.not_existent": "field"
    }
    assert Project.get_matching_column(issue_docs, config) == 'Review in progress'


def test_missing_issues():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()
    project = Project(
        name="test project",
        config=config,
        columns={
            "Queue": ProjectColumn(id="id", name="Queue",
                                   cards=[IssueCard(id="sdf",
                                                    issue=Issue(id="sdf", title="title", number=1))]),
            "Review in progress": ProjectColumn(id="id", name="Review in progress",
                                                cards=[])
        }
    )

    assert len(project.get_all_issue_ids()) == 1
    assert len(project.columns.keys()) == 2

    issue = Issue(
        id="2",
        number=2,
        title="issue title"
    )
    issues = {
        "2": issue
    }
    assert project.find_missing_issue_ids(issues) == {"2"}


def test_removing_issues():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()
    project = Project(
        name="test project",
        config=config,
        columns={
            "Queue": ProjectColumn(id="id", name="Queue",
                                   cards=[IssueCard(id="sdf",
                                                    issue=Issue(id="sdf", title="title", number=1))]),
            "Review in progress": ProjectColumn(id="id", name="Review in progress",
                                                cards=[])
        }
    )

    assert len(project.get_all_issue_ids()) == 1
    assert len(project.columns.keys()) == 2

    issue = Issue(
        id="1",
        number=1,
        title="1"
    )
    issues = {
        1: issue
    }

    class ClientMock(object):
        def delete_project_card(self, **kwargs):
            return

    project.remove_issues(ClientMock, issues, config)
    assert project.get_all_issue_ids() == set()


def test_adding_issue():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()
    project = Project(
        name="test project",
        config=config,
        columns={
            "Queue": ProjectColumn(id="id", name="Queue",
                                   cards=[IssueCard(id="sdf",
                                                    issue=Issue(id="sdf", title="title", number=2))]),
            "Review in progress": ProjectColumn(id="id", name="Review in progress",
                                                cards=[])
        }
    )

    assert len(project.get_all_issue_ids()) == 1
    assert len(project.columns.keys()) == 2

    issue = Issue(
        id="1",
        number=1,
        title="Rony"
    )
    assert issue.priority_rank == 0
    issues = {
        "1": issue
    }

    class ClientMock(object):
        def add_issues_to_project(*args, **kwargs):
            return {
                'addProjectCard': {
                    'cardEdge': {
                        'node': {
                            'id': "1"
                        }
                    }
                }
            }

        def add_to_column(*args, **kwargs):
            return

        def move_to_specific_place_in_column(*args, **kwargs):
            return

    project.add_issues(ClientMock, issues, {"1"}, config)
    assert project.columns['Queue'].cards[0].issue.title == "Rony"

    # testing non existent column
    with pytest.raises(Exception) as err:
        project.add_issue(ClientMock, issue, "non existent", config)
        assert "Did not found a matching column" in err

    issue2 = Issue(
        id="1",
        number=1,
        title="Rony",
        card_id_to_project={
            "1": {
                "project_number": 1
            }
        }
    )
    issues2 = {
        "2": issue2
    }
    project.add_issues(ClientMock, issues2, {"2"}, config)
    assert project.columns['Queue'].cards[0].issue.title == "Rony"


def test_no_card_content():
    cards = _extract_card_node_data({
        "cards": {
            "edges": [
                {
                    "node": {
                        "no": "content"
                    }
                }
            ]
        }
    }, Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini')))
    assert len(cards) == 0


def test_move_issues():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()
    issue = Issue(id="1",
                  title="title",
                  number=1,
                  assignees=["Rony"],
                  labels=["Testing"],
                  card_id_to_project={
                      "sdf": {
                          "project_number": 1
                      }
                  }
                  )
    project = Project(
        name="test project",
        config=config,
        columns={
            "Queue": ProjectColumn(id="id", name="Queue",
                                   cards=[IssueCard(id="sdf",
                                                    issue=issue)]),
            "In progress": ProjectColumn(id="id", name="In progress", cards=[])
        }
    )

    class MockClient(object):
        def add_to_column(*args, **kwargs):
            return

        def move_to_specific_place_in_column(*args, **kwargs):
            return

    project.move_issues(MockClient(), {"1": issue}, config)
    assert project.is_in_column("Queue", "1") is False
    assert project.is_in_column("In progress", "1") is True

    # Move within the same column
    project.move_issues(MockClient(), {"1": issue}, config)
    assert project.is_in_column("Queue", "1") is False
    assert project.is_in_column("In progress", "1") is True
