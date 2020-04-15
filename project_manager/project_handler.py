from project_manager.issue import Issue
from project_manager.project import Project
from project_manager.github_client import GraphQLClient
from project_manager.common import SAME_LEVEL_PRIORITY_IDENTIFIER


class ProjectManager(object):
    DEFAULT_PRIORITY_LIST = ['Critical', 'High', 'Medium', 'Low']

    def __init__(self, project_owner, repository_name, project_number, priority_list=None,
                 client=None, filter_labels=None, filter_milestone=None, must_have_labels=(), cant_have_labels=(),
                 done_column_name='Done', api_key=None):
        self.project_owner = project_owner
        self.repository_name = repository_name
        self.project_number = project_number

        self.priority_list = priority_list if priority_list else self.DEFAULT_PRIORITY_LIST
        self.client = client if client else GraphQLClient(api_key)

        self.filter_labels = filter_labels if filter_labels else []
        self.filter_milestone = filter_milestone

        self.project = self.get_github_project(done_column_name)
        self.matching_issues = self.get_github_issues(must_have_labels, cant_have_labels)  # todo: add the option to add more filters

    @staticmethod
    def is_matching_issue(issue_labels, must_have_labels, cant_have_labels):
        for label in must_have_labels:
            if label not in issue_labels:
                return False

        for label in cant_have_labels:
            if label in issue_labels:
                return False

        return True

    def construct_issue_object(self, github_issues, must_have_labels, cant_have_labels):
        issues = {}
        for edge in github_issues['edges']:
            node_data = edge['node']
            issue_labels = Issue.get_current_labels(node_data['labels']['edges'])
            if self.is_matching_issue(issue_labels, must_have_labels, cant_have_labels):
                issue = Issue(node_data, self.priority_list)
                issues[issue.id] = issue

        return issues

    def get_github_project(self, done_column_name):
        # Todo: known limitation for now, supporting up to 100 cards in each column for now - can be expanded
        response = self.client.get_github_project(owner=self.project_owner,
                                                  name=self.repository_name,
                                                  number=self.project_number)
        project = response.get("repository", {}).get('project', {})

        return Project(project, done_column_name)

    def get_github_issues(self, must_have_labels, cant_have_labels):
        response = self.client.get_github_issues(owner=self.project_owner,
                                                 name=self.repository_name,
                                                 labels=self.filter_labels,
                                                 milestone=self.filter_milestone,
                                                 after=None)
        issues = response.get('repository', {}).get('issues', {})

        while len(response.get('repository', {}).get('issues', {}).get('edges')) >= 100:
            after = response.get('repository', {}).get('issues', {}).get('edges')[-1].get('cursor')
            response = self.client.get_github_issues(owner=self.project_owner,
                                                     name=self.repository_name,
                                                     after=after,
                                                     labels=self.filter_labels,
                                                     milestone=self.filter_milestone)
            issues.get('edges').extend(response.get('repository', {}).get('issues', {}).get('edges'))

        return self.construct_issue_object(issues, must_have_labels, cant_have_labels)

    def add_issues_to_project(self):
        issues_to_add = self.project.find_missing_issue_ids(self.matching_issues)
        self.project.add_issues(self.client, self.matching_issues, issues_to_add)

    def manage(self, add_issues=True, remove_non_matching=True, order_issues=True):
        if add_issues:
            self.add_issues_to_project()

        if remove_non_matching:
            self.project.remove_issues(self.client, self.matching_issues)

        if order_issues:
            self.project.re_order_issues(self.client, self.matching_issues)


def bug_manager():
    priority_list = ['PoC Blocker', 'Critical', 'High', 'Medium', 'Low',
                     f'Customer{SAME_LEVEL_PRIORITY_IDENTIFIER}zendesk']
    manager = ProjectManager(project_owner='demisto',
                             repository_name='etc',
                             project_number=31,
                             priority_list=priority_list,
                             filter_labels=["bug"],
                             must_have_labels=["content"],
                             cant_have_labels=["Playbooks"])
    manager.manage()


if __name__ == "__main__":
    bug_manager()
