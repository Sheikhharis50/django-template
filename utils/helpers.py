from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from types import FunctionType
import logging
import operator
import jwt
import uuid


logger = logging.getLogger("django")


def log(message, level: str = "error") -> None:
    """
    `Arguments`:
        message:[str] - message to show to logs.
        level:[str] - select level of error.
    `Returns`:
        None
    """
    loggers = {
        "debug": logger.debug,
        "error": logger.error,
        "warn": logger.warning,
        "info": logger.info,
        "critical": logger.critical,
    }
    loggers[level.lower()]("%s" % (message))


def call_func(func, *args):
    """
    `Description`:
        Used to call a method safely.
    `Arguments`:
        func:[FunctionType] - method which needs to be run.
    `Returns`:
        response:[Any|None] - method response can be anything.
    """
    if callable(func):
        try:
            return func(*args)
        except Exception as e:
            log(e)
    return None


def find_key(obj: dict = {}, value: Any = "") -> Any:
    """
    `Arguments`:
        obj:[dict] - source where to find.
        value:[Any] - the value to find.
    `Returns`:
        key:[Any] - key which find by key
    """
    try:
        # list out keys and values separately
        key_list = list(obj.keys())
        val_list = list(obj.values())
        # find position of value in values list
        position = val_list.index(value)
        # return positioned key
        return key_list[position]
    except Exception as e:
        log(str(e))

    return value


def tuple_to_dict(t: tuple = ()) -> dict:
    """
    `Arguments`:
        t:[tuple] - source.
    `Returns`:
        kwargs:[dict] - converted dictionary
    """
    kwargs = dict()
    try:
        for index in range(0, len(t), 2):
            kwargs[t[index]] = t[index + 1]
    except IndexError as e:
        pass
    return kwargs


def is_instance(obj: object, class_name: str) -> bool:
    """
    `Arguments`:
        obj:[object] - object of any class.
        class_name:[str] - class_name of object belong to.
    `Returns`:
        Any:[bool] - True if object belongs to that class else False
    """
    if hasattr(obj, "__class__") and obj.__class__.__name__ == class_name:
        return True
    return False


def not_naive_datetime() -> datetime:
    """
    `Arguments`:
        None
    `Returns`:
        Any:[datetime] - not naive datetime
    """
    return timezone.now()


def is_sublist(sub_list: list, main_list: list, method: str = "any") -> bool:
    """
    `Arguments`:
        sub_list:[list] - sub list which we want to find in main list.
        main_list:[list] - main list.
        method:[str] - default set to `any` but we can use `all` too.
    `Returns`:
        Any:[bool] - according to the method we use.
    """
    method = any if method == "any" else all
    return method(item in main_list for item in sub_list)


def truthy(obj1: object, oper: str, obj2: object, type: object = None):
    """
    `Description`:
        Used to check truthy of objects safely.
    `Arguments`:
        obj1:[object] - object of given type.
        oper:[str] - you can use these operators (lt, le, eq, ne, ge, gt).
        obj2:[object] - object.
        type:[object|None] - object of given type.
    `Returns`:
        Any:[bool] - after compare.
    """

    def verify_type():
        if not type:
            return True
        elif type and isinstance(obj1, type) and isinstance(obj2, type):
            return True
        return False

    return verify_type() and call_func(getattr(operator, oper), obj1, obj2)


def with_cache(sec: int = 30):
    """
    `Description`:
        Used to `cache` the response for givent time.
    `Arguments`:
        sec:[int] - seconds.
    `Returns`:
        response:[Any] - method response can be anything.
    """

    def inner(func: FunctionType):
        def wrapper(*args, **kwargs):
            result = cache.get(func.__name__)
            if not result:
                result = func(*args, **kwargs)
                cache.set(func.__name__, result, sec)
                log("Cache for {} is set!".format(func.__name__), "info")
            return result

        return wrapper

    return inner


def remove_cache(func_name: str):
    """
    `Description`:
        Used to remove `cached` function response.
    `Arguments`:
        func_name:[str] - function name.
    `Returns`:
        None
    """
    cache.delete(func_name) if type(func_name) == str else None
    log("Cache for {} is removed!".format(func_name), "info")


def gen_key(n: int = 16) -> str:
    """
    `Description`:
        Used to generate a n-characters token:
        - at least one lowercase character.
        - at least one uppercase character.
        - at least three digits.
    `Arguments`:
        n:[int] - number of characters.
    `Returns`:
        token:[str] - generated token.
    """
    import string
    import secrets

    alphabet = string.ascii_letters + string.digits
    while True:
        token = "".join(secrets.choice(alphabet) for i in range(n))
        if (
            any(c.islower() for c in token)
            and any(c.isupper() for c in token)
            and sum(c.isdigit() for c in token) >= 3
        ):
            return token


def to_uuid(uuid_string: str, version=4) -> Union[uuid.UUID, None]:
    """
    convert to a UUID string and verify if a valid uuid4.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.
    """
    if uuid_string is None:
        return None

    try:
        val = uuid.UUID(uuid_string, version=version)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return None

    # If the uuid_string is a valid hex code,
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a
    # valid uuid4. This is bad for validation purposes.
    return val if val.__str__() == uuid_string else None


def create_token(text: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": text}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=20)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.SIMPLE_JWT.get("OTHER_SIGNING_KEY"),
        algorithm=settings.SIMPLE_JWT.get("ALGORITHM"),
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SIMPLE_JWT.get("OTHER_SIGNING_KEY"),
            algorithms=[settings.SIMPLE_JWT.get("ALGORITHM")],
        )
        return payload.get("sub")
    except Exception as e:
        log(e)
    return None
