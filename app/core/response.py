from rest_framework import (
    status as res_status,
    response,
)
from django.conf import settings


class APIResponse(response.Response):
    """
    Custom API Response
    """

    def __init__(
        self,
        payload={},
        detail=None,
        status=res_status.HTTP_200_OK,
        other_data={},
        template_name=None,
        headers=None,
        exception=False,
        content_type=None if settings.DEBUG else "application/json",
    ):
        super().__init__(
            data=self._gen_response(payload, detail, other_data, status),
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )

    def _gen_response(self, payload, detail, other_data, status):
        data = dict()
        if status < res_status.HTTP_400_BAD_REQUEST:
            payload = dict(data=payload)
        if other_data:
            data.update(other_data)
        if detail:
            data.update(detail=detail)
        data.update(payload)
        return data
