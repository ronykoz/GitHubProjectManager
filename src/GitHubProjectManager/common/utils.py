def get_first_column_issues(client, config):
    response = client.get_first_column_issues(owner=config.project_owner,
                                              name=config.repository_name,
                                              project_number=config.project_number)
    cards_page_info = response['repository']['project']['columns']['nodes'][0]['cards']['pageInfo']
    while cards_page_info['hasNextPage']:
        new_response = client.get_first_column_issues(owner=config.project_owner,
                                                      name=config.repository_name,
                                                      project_number=config.project_number,
                                                      start_cards_cursor=cards_page_info['endCursor'])
        response['repository']['project']['columns']['nodes'][0]['cards']['edges']. \
            extend(new_response['repository']['project']['columns']['nodes'][0]['cards']['edges'])
        cards_page_info = new_response['repository']['project']['columns']['nodes'][0]['cards']['pageInfo']

    return response


def get_column_issues_with_prev_column(client, config, prev_cursor):
    response = client.get_column_issues(owner=config.project_owner,
                                        name=config.repository_name,
                                        project_number=config.project_number,
                                        prev_column_id=prev_cursor)
    cards_page_info = response['repository']['project']['columns']['nodes'][0]['cards']['pageInfo']
    while cards_page_info['hasNextPage']:
        new_response = client.get_column_issues(owner=config.project_owner,
                                                name=config.repository_name,
                                                project_number=config.project_number,
                                                prev_column_id=prev_cursor,
                                                start_cards_cursor=cards_page_info['endCursor'])
        response['repository']['project']['columns']['nodes'][0]['cards']['edges']. \
            extend(new_response['repository']['project']['columns']['nodes'][0]['cards']['edges'])
        cards_page_info = new_response['repository']['project']['columns']['nodes'][0]['cards']['pageInfo']

    return response
