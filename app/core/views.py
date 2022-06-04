from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.request import Request
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions, status

from utils.helpers import log

from app.core.response import APIResponse
from app.core.permissions import IsNotSuperUser
from app.core.pagination import Pagination


class AppBaseView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsNotSuperUser]
    related_fields = ()
    related_many_fields = ()
    http_method_names = []
    required_feilds = ["model"]
    method_serializers = {
        "get": "serializer_view_class",
        "post": "serializer_create_class",
        "put": "serializer_update_class",
        "patch": "serializer_partial_update_class",
        "delete": "serializer_delete_class",
    }
    filters = {"is_hidden": False}
    excludes = {}
    return_data = True

    def __init__(self, **kwargs):
        # http_method_names into lower
        self.http_method_names = [x.lower() for x in self.http_method_names]
        # get serializer_class according to the request method
        if not hasattr(self, "serializer_class"):
            self.serializer_class = self.get_serializer_class()
        # check if the required feilds are recieved.
        self.check_required_feilds()
        super().__init__(**kwargs)

    def __classname__(self):
        return type(self).__name__

    def check_required_feilds(self):
        for feild in self.required_feilds:
            self.get_attr(feild)

    def get_attr(self, attr: str, raise_exception=True):
        if not hasattr(self, attr):
            if raise_exception:
                raise AssertionError(
                    f"`{self.__classname__()}` must have a `{attr}` attribute"
                )
            return None
        return getattr(self, attr)

    def get_queryset(self):
        if not self.request:
            return self.model.objects.none()

        return (
            self.model.objects.prefetch_related(*self.related_many_fields)
            .select_related(*self.related_fields)
            .exclude(**self.excludes)
            .filter(**self.filters)
        )

    def get_serializer_class(self):
        if hasattr(self, "request") and hasattr(self.request, "method"):
            current_method = self.request.method.lower()
            if (
                current_method
                and not current_method == "delete"
                and current_method in self.http_method_names
            ):
                return self.get_attr(self.method_serializers[current_method])

        for method in sorted(self.http_method_names, reverse=True):
            serializer_class = self.get_attr(
                self.method_serializers[method],
                raise_exception=False,
            )
            if serializer_class:
                return serializer_class

        raise AssertionError(
            f"`{self.__classname__()}` must have a `serializer_class` attribute"
        )


class AppView(
    AppBaseView,
    ListCreateAPIView,
):
    http_method_names = ["get", "post"]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    success_msg = "Created Successfully."

    def _list(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            log(str(e))
        return APIResponse(detail="Invalid Data")

    def get(self, request, *args, **kwargs):
        return self._list(request, *args, **kwargs)

    @method_decorator(cache_page(settings.CACHE_FOR_DAY))
    def get_for_day(self, request, *args, **kwargs):
        return self._list(request, *args, **kwargs)

    @method_decorator(cache_page(settings.CACHE_FOR_1H))
    def get_for_hour(self, request, *args, **kwargs):
        return self._list(request, *args, **kwargs)

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        errors = dict()
        if serializer.is_valid():
            try:
                obj = serializer.save()
                if self.return_data:
                    return APIResponse(self.serializer_view_class(obj).data)
                return APIResponse(detail=self.success_msg)
            except exceptions.ValidationError as e:
                errors = e.args[0]
                log(str(errors))
            except Exception as e:
                log(str(e))
        return APIResponse(
            serializer.get_errors(errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class AppDetailView(
    AppBaseView,
    RetrieveUpdateDestroyAPIView,
):
    http_method_names = ["get", "put", "patch", "delete"]

    def get(self, request, pk: str):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(serializer.data)

    def update(self, request, partial=False):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        errors = dict()
        if serializer.is_valid():
            try:
                obj = serializer.save()
                if self.return_data:
                    return APIResponse(self.serializer_view_class(obj).data)
                return APIResponse(detail="Update Successfully.")
            except exceptions.ValidationError as e:
                errors = e.args[0]
                log(str(errors))
            except Exception as e:
                log(str(e))
        return APIResponse(
            serializer.get_errors(errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request: Request, pk: str):
        return self.update(request=request)

    def patch(self, request: Request, pk: str):
        self.kwargs["partial"] = True
        return self.update(request=request, partial=True)

    def delete(self, request: Request, pk: str):
        instance = self.get_object()
        instance.is_hidden = True
        instance.save()
        return APIResponse(detail="Record is Deleted.")


class AppAPIView(APIView):
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        return None


class AppListView(AppAPIView):
    pagination_class = Pagination

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def paginated_response(self, queryset, other_data={}):
        assert hasattr(
            self, "serializer_view_class"
        ), "`serializer_view_class` is not defined"
        assert self.paginator is not None

        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.paginator.get_paginated_response(
                data=self.serializer_view_class(page, many=True).data,
                other_data=other_data,
            )
        else:
            serializer = self.serializer_class(queryset, many=True)
        return APIResponse(payload=serializer.data, other_data=other_data)
