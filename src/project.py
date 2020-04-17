from src.common import OR
from src.configuration import Configuration


class IssueCard(object):
    def __init__(self, id, issue_id, issue_title, cursor=''):
        self.id = id
        self.cursor = cursor
        self.issue_id = issue_id
        self.issue_title = issue_title


class ProjectColumn(object):
    def __init__(self, column_node):
        self.id = column_node['id']
        self.name = column_node['name']

        self.cards = self.extract_card_node_data(column_node)

    @staticmethod
    def is_epic(card_content):
        for label_node in card_content['labels']['edges']:
            if 'Epic' in label_node['node']['name']:
                return True

        return False

    def extract_card_node_data(self, column_node):
        cards = []
        for card in column_node['cards']['edges']:
            card_content = card.get('node', {}).get('content')
            if not card_content or self.is_epic(card_content):
                continue

            cards.append(IssueCard(id=card.get('node', {}).get('id'),
                                   issue_id=card_content['id'],
                                   cursor=card['cursor'],
                                   issue_title=card_content['title']))

        return cards

    def get_all_issue_ids(self):
        return {card.issue_id for card in self.cards}

    def add_card(self, card_id, issue_id, issues, client):
        new_issue = issues[issue_id]
        insert_after_position = len(self.cards) - 1  # In case it should be the lowest issue
        if new_issue > issues[self.cards[0].issue_id]:
            self.cards.insert(0, IssueCard(id=card_id, issue_id=issue_id, issue_title=new_issue.title))
            client.add_to_column(card_id=card_id,
                                 column_id=self.id)
            return

        for i in range(len(self.cards) - 1):
            if issues[self.cards[i].issue_id] > new_issue > issues[self.cards[i + 1].issue_id]:
                insert_after_position = i
                break

        self.cards.insert(insert_after_position + 1,
                          IssueCard(id=card_id, issue_id=issue_id, issue_title=new_issue.title))
        client.move_to_specific_place_in_column(card_id=card_id,
                                                column_id=self.id,
                                                after_card_id=self.cards[insert_after_position].id)

    def get_card_id(self, issue_id):
        for card in self.cards:
            if card.issue_id == issue_id:
                return card.id

        return

    def remove_card(self, card_id):
        for index, card in enumerate(self.cards):
            if card_id == card.id:
                del self.cards[index]
                break


class Project(object):
    def __init__(self, git_hub_project, done_column_name):
        self.all_issues = set()
        self.columns = {}
        for column_node in git_hub_project['columns']['nodes']:
            column = ProjectColumn(column_node)

            self.columns[column.name] = column
            self.all_issues = self.all_issues.union(column.get_all_issue_ids())

        self.done_column_name = done_column_name

    def temp_get_matching_column(self, issue, config: Configuration):
        column_name = ''
        for tested_column_name in config.column_rule_desc_order:
            conditions = config.column_to_rules[tested_column_name]
            is_true = True
            for condition, condition_value in conditions.items():
                try:
                    condition_results = eval(condition)
                except TypeError:
                    is_true = False
                    break

                if isinstance(condition_value, list):  # todo: add the option to have not condition
                    for option in condition_value:
                        if OR in option:
                            options = option.split(OR)
                            if not any([True if option in condition_results else False for option in options]):
                                is_true = False
                                break

                        elif option not in condition_results:
                            is_true = False
                            break

                elif isinstance(condition_value, bool):
                    if condition_value is not bool(condition_results):
                        is_true = False
                        break

                elif condition_value != condition_results:
                    is_true = False
                    break

            if is_true:
                column_name = tested_column_name
                break

        if self.columns.get(column_name):
            column_id = self.columns[column_name].id
        else:
            column_id = ''

        return column_name, column_id

    def find_missing_issue_ids(self, issues):
        issues_in_project_keys = set(self.all_issues)
        all_matching_issues = set(issues.keys())
        return all_matching_issues - issues_in_project_keys

    def add_issues(self, client, issues, issues_to_add, config):
        for issue_id in issues_to_add:
            column_name, column_id = self.get_matching_column(issues[issue_id])
            import ipdb
            ipdb.set_trace()
            column_name, column_id = self.temp_get_matching_column(issues[issue_id], config)
            if column_name not in config.column_names:
                raise Exception(f"Did not found a matching column for your issue, please check your configuration "
                                f"file. The issue was {issues[issue_id].title}")

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

    def get_matching_column(self, issue):  # todo: have this configurable
        column_name = ''
        if 'PendingSupport' in issue.labels or 'PendingVerification' in issue.labels:
            if not self.is_in_column('Pending Support', issue.id):
                column_name = 'Pending Support'

        elif not issue.assignees:
            if not self.is_in_column('Queue', issue.id):
                column_name = 'Queue'

        elif issue.assignees:
            if issue.pull_request and issue.pull_request.review_requested:
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

    def get_current_location(self, issue_id):
        for column_name, column in self.columns.items():
            card_id = column.get_card_id(issue_id)
            if card_id:
                return column_name, card_id

        return None, None

    def re_order_issues(self, client, issues, config):
        # todo: add explanation that we are relying on the github automation to move closed issues to the Done queue
        for issue in issues.values():
            column_name_before, card_id = self.get_current_location(issue.id)
            column_name_after, column_id = self.temp_get_matching_column(issue, config)
            if not column_id or (column_name_after == column_name_before and not config.sort):
                continue

            import ipdb
            ipdb.set_trace()
            print(f"Moving card {issue.title} from {column_name_before} to '{column_name_after}'")
            self.columns[column_name_after].add_card(card_id=card_id,
                                                     issue_id=issue.id,
                                                     issues=issues,
                                                     client=client)

            self.columns[column_name_before].remove_card(card_id)

    def remove_issues(self, client, issues):
        for column in self.columns.values():
            if column.name == self.done_column_name:  # Not going over closed issues
                continue

            for card in column.cards:
                if card.issue_id not in issues:
                    import ipdb
                    ipdb.set_trace()
                    print(f'Removing issue {card.issue_title} from project')
                    client.delete_project_card(card.id)
