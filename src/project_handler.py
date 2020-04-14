from src.issue import Issue
from src.project import Project
from src.github_client import GraphQLClient


def extract_issues_information(github_issues):
    issues = {}
    for edge in github_issues['edges']:
        node_data = edge['node']
        labels = Issue.get_current_labels(node_data['labels']['edges'])
        if 'content' not in labels or 'Playbooks' in labels:
            continue  # In this case we don't need the issue

        issue = Issue(node_data, PRIORITY_LIST)
        issues[issue.id] = issue

    return issues


PRIORITY_LIST = ['PoC Blocker', 'Critical', 'High', 'Medium', 'Low', 'Customer', None]


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


def add_issues_to_project(client, project, issues):
    issues_to_add = project.find_missing_issue_ids(issues)
    project.add_issues(client, issues, issues_to_add)


def process_issue_moves():
    client = GraphQLClient()
    project, issues = get_github_information(client)

    project.add_issues(client, issues)
    project.remove_issues(client, issues)
    project.re_order_issues(client, issues)


if __name__ == "__main__":
    process_issue_moves()
