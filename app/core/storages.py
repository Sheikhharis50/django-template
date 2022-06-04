from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

from utils.helpers import log


class LocalMediaStorage(FileSystemStorage):
    location = settings.MEDIA_LOCATION


class RemoteStaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION
    file_overwrite = False


class RemoteMediaStorage(S3Boto3Storage):
    location = settings.MEDIA_LOCATION
    file_overwrite = True


def delete_file(path: str):
    if default_storage.exists(path):
        default_storage.delete(path)
        log("File deleted: {}".format(path), "info")
        return True
    return False
