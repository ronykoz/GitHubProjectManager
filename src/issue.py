from dateutil.parser import parse
from typing import List, Dict

from src.pull_request import PullRequest


class Issue(object):
    def __init__(self, github_issue: Dict, priority_list: List):
        self.id = github_issue['id']
        self.title = github_issue['title']
        self.number = github_issue['number']
        self.assignees = self.get_assignees(github_issue['assignees']['edges'])
        self.pull_request = self.get_pull_request(github_issue)

        self.labels = self.get_current_labels(github_issue['labels']['edges'])
        self.labels_information = self.extract_labels_information(github_issue)

        self.priority_rank = None  # Todo: add this here
        self.set_priority(priority_list)

    def set_priority(self, priority_list: List):
        for index, priority in enumerate(priority_list):
            if priority in self.labels:
                self.priority_rank = len(priority) - index
                break

        else:
            self.priority_rank = 0

    @staticmethod
    def get_current_labels(label_edges):
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
        if self.priority_rank > other.priority_rank:  # todo: Update the priority to be a dynamic enum
            return True

        elif self.priority_rank == other.priority_rank:
            if self.number < other.number:  # lower issue number means older issue - hence more prioritized
                return True

        return False

    @staticmethod
    def extract_labels_information(issue_node):
        labels = {}
        timeline_nodes = issue_node['timelineItems']['nodes']
        for timeline_node in timeline_nodes:
            if not timeline_node or 'label' not in timeline_node:
                continue

            label = timeline_node['label']['name']
            created_at = parse(timeline_node['createdAt'])

            # Checking if the label was removed
            if 'UnlabeledEvent' in timeline_node and label in labels and labels[label] < created_at:
                del labels[label]
                continue

            if label not in labels or labels[label] < created_at:
                labels[label] = created_at

        return labels
