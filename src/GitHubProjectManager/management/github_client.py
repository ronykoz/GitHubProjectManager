import os

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()


class GraphQLClient(object):
    BASE_URL = 'https://api.github.com'

    def __init__(self, api_key=None):
        api_key = api_key if api_key else os.getenv("GITHUB_TOKEN")  # TODO: add explanation in readme
        sample_transport = RequestsHTTPTransport(
            url=self.BASE_URL + '/graphql',
            use_json=True,
            headers={
                'Authorization': f"Bearer {api_key}"
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

    def get_github_project(self, owner, name, number):
        return self.execute_query('''
        query ($owner: String!, $name: String!, $number: Int!){
          repository(owner: $owner, name: $name) {
            project(number: $number) {
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
        }''', {"owner": owner, "name": name, "number": number})

    def get_github_issues(self, owner, name, after, labels, milestone):
        vars = {"owner": owner, "name": name, "labels": labels, "milestone": milestone, "after": after}
        if not milestone:
            del vars['milestone']
        if not after:
            del vars['after']

        if not labels:
            del vars['labels']
            return self.execute_query('''
                query ($after: String!, $owner: String!, $name: String!, $milestone: String){
                  repository(owner: $owner, name: $name) {
                    issues(first: 100, after:$after, states: OPEN, filterBy:{milestone: $milestone}) {
                      edges {
                        cursor
                        node {
                        comments(last:5){
                            nodes{
                              author{
                                login
                              }
                              body
                              createdAt
                            }
                          }
                          timelineItems(first:30, itemTypes:[LABELED_EVENT, UNLABELED_EVENT, CROSS_REFERENCED_EVENT]){
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
                                      labels(first:5){
                                        nodes{
                                          name
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
                                __typename
                                ... on LabeledEvent {
                                  label{
                                    name
                                  }
                                  createdAt
                                }
                                ... on UnlabeledEvent {
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
                }''', vars)

        return self.execute_query('''
            query ($after: String, $owner: String!, $name: String!, $labels: [String!], $milestone: String){
              repository(owner: $owner, name: $name) {
                issues(first: 100, after:$after, states: OPEN, filterBy:{labels: $labels, milestone: $milestone}) {
                  edges {
                    cursor
                    node {
                      comments(last:5){
                        nodes{
                          author{
                            login
                          }
                          body
                          createdAt
                        }
                      }
                      timelineItems(first:30, itemTypes:[LABELED_EVENT, UNLABELED_EVENT, CROSS_REFERENCED_EVENT]){
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
                                  labels(first:5){
                                    nodes{
                                      name
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
                            __typename
                            ... on LabeledEvent {
                              label{
                                name
                              }
                              createdAt
                            }
                            ... on UnlabeledEvent {
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
            }''', vars)

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

    def add_to_column(self, card_id, column_id):
        variable_dict = {'cardId': card_id, 'columnId': column_id}

        self.execute_query('''
        mutation moveProjectCardAction($cardId: ID!, $columnId: ID!){
          moveProjectCard(input: {cardId: $cardId, columnId: $columnId}) {
            cardEdge{
              node{
                id
              }
            }
          }
        }''', variable_dict)

    def move_to_specific_place_in_column(self, card_id, column_id, after_card_id):
        variable_dict = {'cardId': card_id, 'columnId': column_id, 'afterCardId': after_card_id}

        self.execute_query('''
        mutation moveProjectCardAction($cardId: ID!, $columnId: ID!, $afterCardId: ID!){
          moveProjectCard(input: {cardId: $cardId, columnId: $columnId, afterCardId: $afterCardId}) {
            cardEdge{
              node{
                id
              }
            }
          }
        }''', variable_dict)

    def delete_project_card(self, card_id):
        return self.execute_query('''
        mutation deleteProjectCardAction($cardId: ID!){
          deleteProjectCard(input: {cardId: $cardId}) {
            deletedCardId
          }
        }''', {'cardId': card_id})

    def get_project_columns(self, owner, name, number):
        return self.execute_query('''
        query ($owner: String!, $name: String!, $number: Int!){
      repository(owner: $owner, name: $name) {
        project(number: $number) {
          name
          id
          columns(first: 15) {
            edges{
              cursor
              node {
                name
              }
            }
          }
        }
      }
    }''', {"owner": owner, "name": name, "number": number})

    def get_issue_after_change(self, owner, name, issue_number):
        return self.execute_query('''
        query ($owner: String!, $name: String!, $issueNumber: Int!){
  repository(owner: $owner, name: $name) {
    issue(number: $issueNumber) {
      timelineItems(first: 5, itemTypes: [CROSS_REFERENCED_EVENT]) {
        __typename
        ... on IssueTimelineItemsConnection {
          nodes {
            ... on CrossReferencedEvent {
              willCloseTarget
              source {
                __typename
                ... on PullRequest {
                  assignees(first: 5) {
                    nodes {
                      login
                    }
                  }
                  number
                  reviewDecision
                }
              }
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
      labels(last: 10) {
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
            name
          }
        }
      }
    }
  }
}
''', {"owner": owner, "name": name, "issueNumber": issue_number})

    def get_column_issues(self, owner, name, project_number, prev_column_id, end_cards_cursor=''):
        return self.execute_query('''
        query ($owner: String!, $name: String!, $projectNumber: Int!, $prevColumnID: ID!, $end_cards_cursor: String) {
  repository(owner: $owner, name: $name) {
    project(number: $projectNumber) {
      name
      id
      columns(after: $prevColumnID, first: 1) {
        nodes {
          name
          id
          cards(first: 100, after: $end_cards_cursor) {
            pageInfo {
              endCursor
              hasNextPage
            }
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
}
''', {"owner": owner, "name": name, "projectNumber": project_number, "prevColumnID": prev_column_id,
            "$end_cards_cursor": end_cards_cursor})
