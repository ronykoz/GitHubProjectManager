from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


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
