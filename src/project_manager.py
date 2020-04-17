from src.configuration import Configuration
from src.github_client import GraphQLClient
from src.issue import Issue
from src.project import Project


class ProjectManager(object):
    DEFAULT_PRIORITY_LIST = ['Critical', 'High', 'Medium', 'Low']

    def __init__(self, configuration: Configuration, client=None, api_key=None):
        self.config = configuration
        self.client = client if client else GraphQLClient(api_key)

        self.project = self.get_github_project(self.config.closed_issues_column)
        self.matching_issues = self.get_github_issues()  # todo: add the option to add more filters

    @staticmethod
    def is_matching_issue(issue_labels, must_have_labels, cant_have_labels):
        for label in must_have_labels:
            if label not in issue_labels:
                return False

        for label in cant_have_labels:
            if label in issue_labels:
                return False

        return True

    def construct_issue_object(self, github_issues):
        issues = {}
        for edge in github_issues['edges']:
            node_data = edge['node']
            issue_labels = Issue.get_current_labels(node_data['labels']['edges'])
            if self.is_matching_issue(issue_labels, self.config.must_have_labels, self.config.cant_have_labels):
                issue = Issue(node_data, self.config.priority_list)
                issues[issue.id] = issue

        return issues

    def get_github_project(self, done_column_name):
        # Todo: known limitation for now, supporting up to 100 cards in each column for now - can be expanded
        response = self.client.get_github_project(owner=self.config.project_owner,
                                                  name=self.config.repository_name,
                                                  number=self.config.project_number)
        project = response.get("repository", {}).get('project', {})

        return Project(project, done_column_name)

    def get_github_issues(self):
        response = self.client.get_github_issues(owner=self.config.project_owner,
                                                 name=self.config.repository_name,
                                                 labels=self.config.filter_labels,
                                                 milestone=self.config.filter_milestone,
                                                 after=None)
        issues = response.get('repository', {}).get('issues', {})

        while len(response.get('repository', {}).get('issues', {}).get('edges')) >= 100:
            after = response.get('repository', {}).get('issues', {}).get('edges')[-1].get('cursor')
            response = self.client.get_github_issues(owner=self.config.project_owner,
                                                     name=self.config.repository_name,
                                                     after=after,
                                                     labels=self.config.filter_labels,
                                                     milestone=self.config.filter_milestone)
            issues.get('edges').extend(response.get('repository', {}).get('issues', {}).get('edges'))

        return self.construct_issue_object(issues)

    def add_issues_to_project(self):
        issues_to_add = self.project.find_missing_issue_ids(self.matching_issues)
        self.project.add_issues(self.client, self.matching_issues, issues_to_add, self.config)

    def manage(self):
        if self.config.remove:  # Better to first remove issues that should not be in the board
            self.project.remove_issues(self.client, self.matching_issues)

        if self.config.add:
            self.add_issues_to_project()

        if self.config.move:
            self.project.re_order_issues(self.client, self.matching_issues, self.config)


def bug_manager_config():
    config = Configuration(conf_file_path='project_manager/project_conf.ini')
    config.load_properties()
    manager = ProjectManager(configuration=config)
    manager.manage()


if __name__ == "__main__":
    bug_manager_config()
