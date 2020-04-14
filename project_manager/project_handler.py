from project_manager.issue import Issue
from project_manager.project import Project
from project_manager.github_client import GraphQLClient


class ProjectManager(object):
    DEFAULT_PRIORITY_LIST = ['Critical', 'High', 'Medium', 'Low']

    def __init__(self, project_owner, repository_name, project_number, priority_list=None, client=None):
        self.project_owner = project_owner
        self.repository_name = repository_name
        self.project_number = project_number

        self.priority_list = priority_list if priority_list else self.DEFAULT_PRIORITY_LIST
        self.client = client if client else GraphQLClient()

        self.project = self.get_github_project()
        self.matching_issues = self.get_github_issues()  # todo: add the option to add more filters

    def construct_issue_object(self, github_issues):
        issues = {}
        for edge in github_issues['edges']:
            node_data = edge['node']
            labels = Issue.get_current_labels(node_data['labels']['edges'])
            if 'content' not in labels or 'Playbooks' in labels:
                continue  # In this case we don't need the issue

            issue = Issue(node_data, self.priority_list)
            issues[issue.id] = issue

        return issues

    def get_github_project(self):
        response = self.client.get_github_project(owner=self.project_owner,
                                                  name=self.repository_name,
                                                  number=self.project_number)
        project = response.get("repository", {}).get('project', {})

        return Project(project)

    def get_github_issues(self):
        response = self.client.get_github_issues(owner=self.project_owner,
                                                 name=self.repository_name)
        issues = response.get('repository', {}).get('issues', {})

        while len(response.get('repository', {}).get('issues', {}).get('edges')) > 0:
            after = response.get('repository', {}).get('issues', {}).get('edges')[-1].get('cursor')
            issues.get('edges').extend(response.get('repository', {}).get('issues', {}).get('edges'))
            response = self.client.get_github_issues_with_after(owner=self.project_owner,
                                                                name=self.repository_name,
                                                                after=after)

        return self.construct_issue_object(issues)

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


def bug_manger():
    priority_list = ['PoC Blocker', 'Critical', 'High', 'Medium', 'Low', 'Customer']
    manager = ProjectManager(project_owner='demisto',
                             repository_name='etc',
                             project_number=31,
                             priority_list=priority_list)
    manager.manage()


if __name__ == "__main__":
    bug_manger()
