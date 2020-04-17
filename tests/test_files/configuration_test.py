import os
import pytest

from src.configuration import Configuration


MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


def test_loading_configuration():
    configuration = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    configuration.load_properties()
    
    assert configuration.closed_issues_column == 'Done'
    assert configuration.project_owner == 'ronykoz'
    assert configuration.repository_name == 'test'
    assert configuration.project_number == 1
    assert configuration.priority_list == ['Critical', 'High', 'Medium', 'Low', 'Customer|||zendesk']
    assert configuration.filter_labels == ['bug']
    assert configuration.filter_milestone == ''
    assert configuration.must_have_labels == ['test']
    assert configuration.cant_have_labels == ['not test']
    assert configuration.column_names == ['Queue', 'In progress', 'Review in progress', 'Waiting for Docs']
    assert configuration.column_rule_desc_order == ['Queue', 'Waiting for Docs', 'Review in progress', 'In progress']

    assert configuration.remove is True
    assert configuration.add is True
    assert configuration.move is True
    assert configuration.sort is False

    assert configuration.column_to_rules['Waiting for Docs']['issue.pull_request.review_requests'] is True
    assert configuration.column_to_rules['Waiting for Docs']['issue.pull_request.assignees'] == ['ronykoz']

def test_loading_illegal_configuration():
    configuration = Configuration(os.path.join(MOCK_FOLDER_PATH, 'illegal_conf.ini'))
    with pytest.raises(ValueError) as exception:
        configuration.load_properties()
        assert 'You have either added a section which is not in the column_names key' in exception

    configuration = Configuration(os.path.join(MOCK_FOLDER_PATH, 'illegal_query_conf.ini'))
    with pytest.raises(ValueError) as exception:
        configuration.load_properties()
        assert 'You have entered an illegal query' in exception
