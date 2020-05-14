[![](https://github.com/ronykoz/GitHubProjectManager/workflows/Python%20package/badge.svg)](https://github.com/ronykoz/GitHubProjectManager/actions?query=branch%3Amaster)
[![Coverage Status](https://coveralls.io/repos/github/ronykoz/GitHubProjectManager/badge.svg?branch=add-coverage)](https://coveralls.io/github/ronykoz/GitHubProjectManager?branch=add-coverage)

# GitHubProjectManager
This tool will help you maintain and organize your GitHub project using an automation tool.

## Use case
In case you work with GitHub projects, and maintain a board for your project this tool is for you.
As we offer a functionality of managing your board in GitHub project boards.
This is by searching for the issues you wish to include in the board(By a set of filter you provide) and placing them in the right place in your board for you - both in the correct column and the correct place within the column.

The supported functionality is:
* Adding new issues to your board.
* Moving issues to the correct column of your project, with the priority in mind.
* Sorting your issues within your existing columns by their priorities and creation times.
* Removing issues that fail to meet your issue filters.
___
In order to configure GitHubProjectManager you will need to create an `.ini` file, here is an example:
```buildoutcfg
[General]
closed_issues_column = Done
project_owner = ronykoz
repository_name = test
project_number = 1
priority_list = Critical,High,Medium,Low
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
The keys listed in the column section are the attributes of the classes which represent the issue you are working on. For a more detailed explanation please click [here](https://github.com/ronykoz/GitHubProjectManager/blob/master/docs/ini_file.md)


### GitHub Actions
In order to use this in a github action please follow this [documentation](https://github.com/ronykoz/GitHubProjectManager/blob/master/docs/ini_file.md).

___
### Usage
There are three options to run the tool:
1. Configure an `.ini` file like described above and then using the `GitHubProjectManager manage -c <path to ini>` command or the `wehbhook-manage` command which is used for events.
2. Import the code and create some more custom rules for your self, like importing issues from another board(FYI this will be added to the tool as well).
3. GitHub actions - In order to use this in a github action please follow this [documentation](https://github.com/ronykoz/GitHubProjectManager/blob/master/docs/GitHub_Action_usage.md).

#### Token
In any solution you will have to set an envioroonment variable `GITHUB_TOKEN` which is the token you will generate in order for the tool to connect to your GitHub project.
Although we do offer the option to pass that along with your client object while taking the API option(Usage case number 2).
