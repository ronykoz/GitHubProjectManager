class PullRequest(object):
    def __init__(self, pull_request_node):
        self.number = pull_request_node['source']['number']
        self.assignees = self.get_assignees(pull_request_node['source']['assignees']['nodes'])
        self.labels = self.get_labels(pull_request_node['source']['labels']['nodes'])
        self.review_requested = self.is_review_requested(pull_request_node['source'])
        self.review_completed = False if pull_request_node['source']['reviewDecision'] != 'APPROVED' else True

    @staticmethod
    def is_review_requested(pull_request_source):
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

    @staticmethod
    def get_labels(label_nodes):
        labels = []
        for label in label_nodes:
            if label:
                labels.append(label['name'])

        return labels
