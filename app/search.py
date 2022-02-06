from flask import current_app


def add_to_index(index: str, model) -> None:
    """Adds model entry to index"""

    if not current_app.elasticsearch:
        return None

    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)

    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index: str, model) -> None:
    """Removes model entry from index"""

    if not current_app.elasticsearch:
        return None

    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index: str, string_to_search: str, page_number: int, objects_per_page: int) -> (list, int):
    """
    Searches for {query} and paginates the result:
    returns list of search results ids and total number of results
    """

    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index=index,
        body={
            'query': {'multi_match': {'query': string_to_search, 'fields': ['*']}},
            'from': (page_number - 1) * objects_per_page, 'size': objects_per_page
        })

    search_result_ids = [int(hit['_id']) for hit in search['hits']['hits']]

    return search_result_ids, search['hits']['total']['value']
