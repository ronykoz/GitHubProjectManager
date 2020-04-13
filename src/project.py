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