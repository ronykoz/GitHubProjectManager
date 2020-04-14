import requests
from dateutil.parser import parse
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()


# Todo: known limitation for now, supporting up to 100 cards in each column for now - can be expanded

class GraphQLClient(object):
    BASE_URL = 'https://api.github.com'

    def __init__(self):
        sample_transport = RequestsHTTPTransport(
            url=self.BASE_URL + '/graphql',
            use_json=True,
            headers={
                'Authorization': "Bearer "
            },
            verify=False
        )
        self.client = Client(
            retries=3,
            transport=sample_transport,
            fetch_schema_from_transport=True,
        )

    def execute_query(self, query, variable_values=None):
        gql_query = gql(query)
        response = self.client.execute(gql_query, variable_values=variable_values)
        return response

    def get_github_project(self):
        return self.execute_query('''
        {
          repository(owner: "demisto", name: "etc") {
            project(number: 31) {
              name
              id
              columns(first: 30) {
                  nodes {
                    name
                    id
                    cards(first: 100) {
                      edges {
                        cursor
                        node {
                          note
                          state
                          id
                          content {
                            ... on Issue {
                              id
                              number
                              title
                              labels(first: 10) {
                                edges {
                                  node {
                                    name
                                  }
                                }
                              }
                            }
                            ... on PullRequest {
                              id
                              number
                              title
                            }
                          }
                        }
                      }
                    }
                  }
              }
            }
          }
        }''')

    def get_github_issues_with_after(self, after=''):
        return self.execute_query('''
            query ($after: String!){
              repository(owner: "demisto", name: "etc") {
                issues(first: 100, after:$after, states: OPEN, labels:"bug") {
                  edges {
                    cursor
                    node {
                      timelineItems(first:30, itemTypes:[LABELED_EVENT, CROSS_REFERENCED_EVENT]){
                        __typename
                        ... on IssueTimelineItemsConnection{
                          nodes {
                            ... on CrossReferencedEvent {
                              willCloseTarget
                              source {
                                __typename 
                                ... on PullRequest {
                                  state
                                  assignees(first:10){
                                    nodes{
                                      login
                                    }
                                  }
                                  reviewRequests(first:1){
                                    totalCount
                                  }
                                  reviews(first:1){
                                    totalCount
                                  }
                                  number
                                  reviewDecision
                                }
                              }
                            }
                            ... on LabeledEvent {
                              label{
                                name
                              }
                              createdAt
                            }
                          }
                        }
                      }
                      title
                      id
                      number
                      milestone {
                        title
                      }
                      labels(first: 10) {
                        edges {
                          node {
                            name
                          }
                        }
                      }
                      assignees(last: 10) {
                        edges {
                          node {
                            id
                            login
                          }
                        }
                      }
                    }
                  }
                }
              }
            }''', {"after": after})

    def get_github_issues(self):
        return self.execute_query('''
            query {
              repository(owner: "demisto", name: "etc") {
                issues(first: 100, states: OPEN, labels:"bug") {
                  edges {
                    cursor
                    node {
                      timelineItems(first:30, itemTypes:[LABELED_EVENT, CROSS_REFERENCED_EVENT]){
                        __typename
                        ... on IssueTimelineItemsConnection{
                          nodes {
                            ... on CrossReferencedEvent {
                              willCloseTarget
                              source {
                                __typename 
                                ... on PullRequest {
                                  state
                                  assignees(first:10){
                                    nodes{
                                      login
                                    }
                                  }
                                  reviewRequests(first:1){
                                    totalCount
                                  }
                                  reviews(first:1){
                                    totalCount
                                  }
                                  number
                                  reviewDecision
                                }
                              }
                            }
                            ... on LabeledEvent {
                              label{
                                name
                              }
                              createdAt
                            }
                          }
                        }
                      }
                      title
                      id
                      number
                      milestone {
                        title
                      }
                      labels(first: 10) {
                        edges {
                          node {
                            name
                          }
                        }
                      }
                      assignees(last: 10) {
                        edges {
                          node {
                            id
                            login
                          }
                        }
                      }
                    }
                  }
                }
              }
            }''')

    def add_issues_to_project(self, issue_id, column_id):
        return self.execute_query('''
        mutation addProjectCardAction($contentID: ID!, $columnId: ID!){
          addProjectCard(input: {contentId: $contentID, projectColumnId: $columnId}) {
            cardEdge{
              node{
                id
              }
            }
          }
        }''', {'contentID': issue_id, 'columnId': column_id})

    def move_issue_in_project(self, card_id, column_id, after_card_id=''):
        #todo: afterCardId
        self.execute_query('''
        mutation moveProjectCardAction($cardId: ID!, $columnId: ID!, $afterCardId: ID!){
          moveProjectCard(input: {cardId: $cardId, columnId: $columnId, afterCardId: $afterCardId}) {
            cardEdge{
              node{
                id
              }
            }
          }
        }''', {'cardId': card_id, 'columnId': column_id, 'afterCardId': after_card_id})

    def delete_project_card(self, card_id):
        return self.execute_query('''
        mutation deleteProjectCardAction($cardId: ID!){
          deleteProjectCard(input: {cardId: $cardId}) {
            deletedCardId
          }
        }''', {'cardId': card_id})


class IssueCard(object):
    def __init__(self, id, issue_id, cursor=''):
        self.id = id
        self.cursor = cursor
        self.issue_id = issue_id


class ProjectColumn(object):
    def __init__(self, column_node, priority_list):
        self.id = column_node['id']
        self.name = column_node['name']
        self.cards = []
        self.priority_list = priority_list

        self.extract_card_node_data(column_node)  # todo: convert to list

    @staticmethod
    def is_epic(card_content):
        for label_node in card_content['labels']['edges']:
            if 'Epic' in label_node['node']['name']:
                return True

        return False

    def extract_card_node_data(self, column_node):
        for card in column_node['cards']['edges']:
            card_content = card.get('node', {}).get('content')
            if not card_content or self.is_epic(card_content):
                continue

            self.cards.append(IssueCard(id=card.get('node', {}).get('id'),
                                        issue_id=card_content['id'],
                                        cursor=card['cursor']))

    def get_all_issue_ids(self):
        return {card.issue_id for card in self.cards}

    def get_issue_priority(self, issue):
        for priority in self.priority_list:
            if priority in issue.labels:
                return priority

        return

    def is_right_card_location(self, new_issue, next_issue, prev_issue=None):
        issue_priority = self.get_issue_priority(new_issue)
        for priority in self.priority_list:
            # First place handling
            if priority and not prev_issue:
                if priority in new_issue.labels and priority not in next_issue.labels:
                    return True

                if priority in new_issue.labels and priority in next_issue.labels and new_issue.number < \
                        next_issue.numsber:
                    return True

                return False

            #todo: handle bigger priority

            # Priority handling for High(prev) - Not High(New) - High(Next)
            if priority in prev_issue.labels and priority in next_issue.labels and priority not in new_issue.labels:
                return False

            # The same priority handling
            if priority in prev_issue.labels and priority in new_issue.labels and priority in next_issue.labels:
                if prev_issue.number < new_issue.number < next_issue.number:
                    return True

                return False

            # Priority switch handling
            if priority in prev_issue.labels and priority in new_issue.labels and priority not in next_issue.labels:
                return True

            if priority not in prev_issue.labels and priority in new_issue.labels and priority in next_issue.labels:
                if new_issue.number < next_issue.number:
                    return True

                return False

            # No special priority handling
            if not priority and all([label not in self.priority_list for label in new_issue.labels]):
                if prev_issue and prev_issue.number < new_issue.number < next_issue.number:
                    return True

                elif new_issue.number < next_issue.number:
                    return True

                return False

        return False

    def add_card(self, card_id, issue_id, issues, client):
        new_issue = issues[issue_id]
        insert_after_position = len(self.cards) - 1  # In case it should be the lowest issue
        if self.is_right_card_location(new_issue, issues[self.cards[0].issue_id]):
            self.cards.insert(0, IssueCard(id=card_id, issue_id=issue_id))
            client.move_issue_in_project(card_id=card_id,
                                         column_id=self.id)
            return

        for i in range(len(self.cards) - 1):
            if self.is_right_card_location(new_issue,
                                           issues[self.cards[i + 1].issue_id],
                                           issues[self.cards[i].issue_id]):
                insert_after_position = i
                break

        self.cards.insert(insert_after_position + 1,
                          IssueCard(id=card_id, issue_id=issue_id))
        client.move_issue_in_project(card_id=card_id,
                                     column_id=self.id,
                                     after_card_id=self.cards[insert_after_position].id)

    def get_card_id(self, issue_id):
        for card in self.cards:
            if card.issue_id == issue_id:
                return card.id

        return


class Project(object):
    PRIORITY_LIST = ['Critical', 'High', 'Medium', 'Low', 'Customer', None]

    def __init__(self, git_hub_project):
        self.all_issues = set()
        self.columns = {}
        for column_node in git_hub_project['columns']['nodes']:
            column = ProjectColumn(column_node, self.PRIORITY_LIST)

            self.columns[column.name] = column
            self.all_issues = self.all_issues.union(column.get_all_issue_ids())

    def find_missing_issue_ids(self, issues):
        issues_in_project_keys = set(self.all_issues)
        all_matching_issues = set(issues.keys())
        return all_matching_issues - issues_in_project_keys

    def add_issues(self, client, issues):
        missing_issue_ids = self.find_missing_issue_ids(issues)
        for issue_id in missing_issue_ids:
            column_name, column_id = self.get_matching_column(issues[issue_id])

            print("Adding issue '{}' to column '{}'".format(issues[issue_id].title, column_name))
            response = client.add_issues_to_project(issue_id, column_id)
            card_id = response['addProjectCard']['cardEdge']['node']['id']
            self.columns[column_name].add_card(card_id=card_id,
                                               issue_id=issue_id,
                                               issues=issues,
                                               client=client)

    def is_in_column(self, column_name, issue_id):
        if issue_id in self.columns[column_name].get_all_issue_ids():
            return True

        return False

    def get_matching_column(self, issue):
        column_name = ''
        if 'PendingSupport' in issue.labels or 'PendingVerification' in issue.labels:
            if not self.is_in_column('Pending Support', issue.id):
                column_name = 'Pending Support'

        elif not issue.assignees:
            if not self.is_in_column('Queue', issue.id):
                column_name = 'Queue'

        elif issue.assignees:
            if issue.pull_request and issue.pull_request.review_requests:
                if issue.pull_request.review_completed and 'kirbles19' in issue.pull_request.assignees:
                    if not self.is_in_column('Waiting for Docs', issue.id):
                        column_name = 'Waiting for Docs'

                else:
                    if not self.is_in_column('Review in progress', issue.id):
                        column_name = 'Review in progress'

            else:
                if not self.is_in_column('In progress', issue.id):
                    column_name = 'In progress'

        if self.columns.get(column_name):
            column_id = self.columns[column_name].id
        else:
            column_id = ''

        return column_name, column_id

    def get_card_id(self, issue_id):
        for column in self.columns.values():
            card_id = column.get_card_id(issue_id)
            if card_id:
                return card_id

    def re_order_issues(self, client, issues):
        for issue in issues.values():
            column_name, column_id = self.get_matching_column(issue)  # Todo: Add card id to this process ?
            if not column_id:
                continue

            card_id = self.get_card_id(issue.id)
            print(f"Moving card {issue.title} to '{column_name}'")
            self.columns[column_name].add_card(card_id=card_id,
                                               issue_id=issue.id,
                                               issues=issues,
                                               client=client)

    def remove_issues(self, client, issues):
        for column in self.columns.values():
            if column.name == 'Done':
                continue

            for card in column.cards:
                if card.issue_id not in issues:
                    print(f'Removing issue {card.issue_id} from project')
                    client.delete_project_card(card.id)


class PullRequest(object):
    def __init__(self, pull_request_node):
        self.number = pull_request_node['source']['number']
        self.assignees = self.get_assignees(pull_request_node['source']['assignees']['nodes'])
        self.review_requests = self.is_review_ready(pull_request_node['source'])
        self.review_completed = False if pull_request_node['source']['reviewDecision'] != 'APPROVED' else True

    @staticmethod
    def is_review_ready(pull_request_source):
        if pull_request_source['reviewRequests']['totalCount'] or pull_request_source['reviews']['totalCount']:
            return True

        else:
            return False

    @staticmethod
    def get_assignees(assignee_nodes):
        assignees = []
        for assignee in assignee_nodes:
            if assignee:
                assignees.append(assignee['login'])

        return assignees


class Issue(object):
    def __init__(self, github_issue):
        self.id = github_issue['id']
        self.title = github_issue['title']
        self.number = github_issue['number']
        self.labels = self.get_labels(github_issue['labels']['edges'])
        self.assignees = Issue.get_assignees(github_issue['assignees']['edges'])
        self.pull_request = self.get_pull_request(github_issue)

        self.labels_to_date = self.extract_labels(github_issue)

        self.priority = None  # Todo: add this here

    @staticmethod
    def get_labels(label_edges):
        label_names = []
        for edge in label_edges:
            node_data = edge.get('node')
            if node_data:
                label_names.append(node_data['name'])

        return label_names

    @staticmethod
    def get_assignees(assignee_edges):
        assignee_id_to_name = {}
        for edge in assignee_edges:
            node_data = edge.get('node')
            if node_data:
                assignee_id_to_name[node_data['id']] = node_data['login']

        return assignee_id_to_name

    @staticmethod
    def get_pull_request(issue_node):
        timeline_nodes = issue_node['timelineItems']['nodes']
        for timeline_node in timeline_nodes:
            if not timeline_node or 'willCloseTarget' not in timeline_node:
                continue

            if timeline_node['willCloseTarget'] and timeline_node['source']['__typename'] == 'PullRequest' \
                    and timeline_node['source']['state'] == 'OPEN':

                return PullRequest(timeline_node)

    def __gt__(self, other):
        if self.priority > other.priority:  # todo: Update the priority to be a dynamin enum
            return True

        elif self.priority == other.priority:
            if self.number < other.number:  # lower issue number means older issue - hence more prioritized
                return True

        return False

    @staticmethod
    def extract_labels(issue_node):
        labels = {}
        timeline_nodes = issue_node['timelineItems']['nodes']
        for timeline_node in timeline_nodes:
            if not timeline_node or 'label' not in timeline_node:
                continue

            label = timeline_node['label']['name']
            created_at = parse(timeline_node['createdAt'])
            if label not in labels or labels[label] < created_at:
                labels[label] = created_at

        return labels


def extract_issues_information(github_issues):
    issues = {}
    for edge in github_issues['edges']:
        node_data = edge['node']
        labels = Issue.get_labels(node_data['labels']['edges'])
        if 'content' not in labels or 'Playbooks' in labels:
            continue  # In this case we don't need the issue

        issue = Issue(node_data)
        issues[issue.id] = issue

    return issues


def get_github_information(client):
    response = client.get_github_project()
    project = response.get("repository", {}).get('project', {})

    response = client.get_github_issues()
    issues = response.get('repository', {}).get('issues', {})

    while len(response.get('repository', {}).get('issues', {}).get('edges')) > 0:
        after = response.get('repository', {}).get('issues', {}).get('edges')[-1].get('cursor')
        issues.get('edges').extend(response.get('repository', {}).get('issues', {}).get('edges'))
        response = client.get_github_issues_with_after(after=after)

    project = Project(project)
    issues = extract_issues_information(issues)
    return project, issues


def process_issue_moves():
    client = GraphQLClient()
    project, issues = get_github_information(client)

    project.add_issues(client, issues)
    project.remove_issues(client, issues)
    project.re_order_issues(client, issues)


# todo add ut

if __name__ == "__main__":
    process_issue_moves()
