from rest_framework.pagination import PageNumberPagination
from .response import APIResponse


class StandardPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "size"
    max_page_size = 1000


class Pagination(StandardPagination):
    def get_paginated_response(self, data, other_data={}):
        return APIResponse(
            payload=data,
            other_data={
                "count": self.page.paginator.count,
                "next": self.page.has_next(),
                "previous": self.page.has_previous(),
                **other_data,
            },
        )
