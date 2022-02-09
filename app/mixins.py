from flask import url_for

from app import db
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin:
    """Mixin performing elasticsearch"""

    @classmethod
    def search(cls, string_to_search: str, page_number: int, objects_per_page: int):
        """Searches for {string_to_search} and returns model instances of the search result paginated"""

        ids, total = query_index(cls.__tablename__, string_to_search, page_number, objects_per_page)
        if not total:
            return cls.query.filter_by(id=0), 0
        when = [(ids[i], i) for i in range(len(ids))]

        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session) -> None:
        """Saves changes to update the Elasticsearch index later"""

        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session) -> None:
        """Updates the Elasticsearch index"""

        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)

        session._changes = None

    @classmethod
    def reindex(cls) -> None:
        """Refreshes an index with all the data from the model"""

        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class PaginatedAPIMixin(object):
    """Mixin for API pagination"""

    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs) -> dict:
        """Returns dictionary for API with data paginated"""

        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) if resources.has_prev else None,
            }
        }

        return data
