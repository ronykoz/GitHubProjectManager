from configparser import ConfigParser

from project_manager.common import AND, OR


class Configuration(object):
    DELIMITER = ','
    LIST_ATTRIBUTES = [
        'priority_list',
        'filter_labels',
        'must_have_labels',
        'cant_have_labels',
        'column_order'
    ]
    PERMITTED_QUERIES = [
        'issue.assignees',
        'issue.pull_request',
        'issue.pull_request.review_requests',
        'issue.labels',
        'issue.pull_request.review_completed',
        'issue.pull_request.assignees'
    ]  # TODO: load this list dynamicaly from the project

    SECTION_NAME_ERROR = 'You have either added a section which is not in the column_order key in the ' \
                         'General section, or miss-spelled. The section name is {}'
    ILLEGAL_QUERY = "You have entered an illegal query - {}, the possible options are:\n" + '\n'.join(PERMITTED_QUERIES)

    def __init__(self, conf_file_path):
        self.config = ConfigParser()
        self.config.read(conf_file_path)

        # General
        self.closed_issues_column = ''
        self.project_owner = ''
        self.repository_name = ''
        self.project_number = None
        self.priority_list = []
        self.filter_labels = []
        self.must_have_labels = []
        self.cant_have_labels = []
        self.column_order = []

        # Conditional
        self.column_to_rules = {}

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def custom_set_attr(self, key, value):
        if self.DELIMITER in value:
            value = value.split(self.DELIMITER)

        elif value.isdigit():
            value = int(value)

        if key in self.LIST_ATTRIBUTES and not isinstance(value, list):
            value = [value]

        self.__setattr__(key, value)

    def load_general_properties(self):
        for key in self.config['General']:
            if key not in self.__dict__:
                raise ValueError(f'Provided illegal key - {key} in General section')

            self.custom_set_attr(key, self.config['General'][key])

    def load_column_rules(self):
        for section in self.config.sections():
            if 'General' == section:
                continue

            if section not in self.column_order:
                raise ValueError(self.SECTION_NAME_ERROR.format(section))

            self.column_to_rules[section] = {}
            for key in self.config[section]:
                if key not in self.PERMITTED_QUERIES:
                    raise ValueError(self.ILLEGAL_QUERY.format(key))
                value = self.config[section][key]
                if self.DELIMITER in value:
                    value = [value]

                if value in ['true', 'false']:
                    value = bool(value)

                self.column_to_rules[section][key] = value

    def load_properties(self):
        self.load_general_properties()
        self.load_column_rules()
        print(self.column_to_rules)


if __name__ == '__main__':
    conf = Configuration('project_manager/project_conf.ini')
    conf.load_properties()
