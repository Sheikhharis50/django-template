from rest_framework import serializers

from utils.helpers import log


def list_to_key_value(payload):
    if isinstance(payload, dict):
        item = dict()
        for key, value in payload.items():
            item[key] = list_to_key_value(value)
        return item
    if isinstance(payload, list):
        items = list()
        for item in payload:
            if item and isinstance(item, dict):
                items.append(list_to_key_value(item))
            elif item:
                return item
        return items if len(items) else None
    return payload


class AppSerializer(serializers.Serializer):
    error_msg = "Invalid Data"
    with_errors = True

    def _check_passed_errors(self, passed_errors):
        if type(passed_errors) == str:
            passed_errors = dict(feild_not_specified=passed_errors)
        elif type(passed_errors) != dict:
            passed_errors = {}
        return passed_errors

    def _gen_error(self, msg=None, with_errors=True):
        self.with_errors = with_errors
        error_msg = msg if msg else self.error_msg
        self.error_msg = error_msg
        raise serializers.ValidationError(error_msg)

    def get_errors(self, passed_errors: dict = {}, error_msg: str = None):
        errors = super().errors
        errors.update(self._check_passed_errors(passed_errors))
        try:
            errors = list_to_key_value(errors)
        except Exception as e:
            log(str(e))
        res_data = dict(detail=error_msg if error_msg else self.error_msg)
        if self.with_errors:
            res_data.update({"errors": errors})
        return res_data


class AppModelSerializer(serializers.ModelSerializer, AppSerializer):
    def check_change(self, instance, data: dict):
        fields = self.Meta.fields
        return [
            field
            for field in fields
            if data.get(field, "None") != "None"
            and getattr(instance, field) != data.get(field)
        ]

    def set_validated_data(
        self,
        instance: object,
        validated_data: dict = {},
        excludes: list = [],
        save=True,
    ):
        for key, value in validated_data.items():
            if value and hasattr(instance, key) and not key in excludes:
                setattr(instance, key, value)
        if save:
            instance.save()
        return instance
