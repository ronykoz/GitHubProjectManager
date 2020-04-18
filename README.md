[![](https://github.com/ronykoz/GitHubProjectManager/workflows/Python%20package/badge.svg)](https://github.com/ronykoz/GitHubProjectManager/actions?query=branch%3Amaster)
[![Coverage Status](https://coveralls.io/repos/github/ronykoz/GitHubProjectManager/badge.svg?branch=add-coverage)](https://coveralls.io/github/ronykoz/GitHubProjectManager?branch=add-coverage)

# GitHubProjectManager
This tool will help you maintain your project in GitHub with ease.

We offer a functionality of managing your board in GitHub project.
This is by searching for the issues you define, The supported functionality is:
* adding - Adding new issues to your board.
* moving - Moving issues to the correct column of your project.
* sorting - Sorting your issues within your existing columns.
* removing - Removing issues that fail to meet your issue filters.

___
In order to configure GitHubProjectManager you will neet to create an `.ini` file, here is an example:
```buildoutcfg
[General]
closed_issues_column = Done
project_owner = ronykoz
repository_name = test
project_number = 1
priority_list = Critical,High,Medium,Low,Customer|||zendesk
filter_labels=bug
must_have_labels=test
cant_have_labels=not test
column_names = Queue,In progress,Review in progress,Waiting for Docs
column_rule_desc_order = Queue,Waiting for Docs,Review in progress,In progress

[Actions]
remove
add
move

[Queue]
issue.assignees = false

[In progress]
issue.assignees = true

[Review in progress]
issue.assignees = true
issue.pull_request = true
issue.pull_request.review_requested = true

[Waiting for Docs]
issue.assignees = true
issue.pull_request = true
issue.pull_request.review_requested = true
issue.pull_request.review_completed = true
issue.pull_request.assignees = ronykoz

```
While the General and Actions sections must be in the `.ini` the rest of the sections are dynamic, and each represents the rules for each of your columns.
The keys listed in the column section are the attributes of the classes which represent the issue you are working on.

___
### Usage
There are two options to run the tool:
1. Configure an `.ini` file like described above and then using the `GitHubProjectManager manage -c <path to ini>` command - better with a cronjob to order your board automatically.
2. Import the code and create some more custom rules for your self, like importing issues from another board(FYI this will be added to the tool as well).
