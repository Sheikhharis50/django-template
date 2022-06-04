from django.db import connection, IntegrityError, transaction
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from types import FunctionType
from typing import Any, Tuple, Union, Dict, List
from asgiref.sync import async_to_sync, sync_to_async
import asyncio

from app_accounts.authentication import SafeJWTAuthentication

from utils.helpers import log


@transaction.atomic
def run_with_atomic(
    main_task: FunctionType,
    main_task_args: Tuple[Any],
    handle_exception: FunctionType = None,
    handle_exception_args: Tuple[Any] = None,
):
    """
    `Description`:
        Used to call a method with attomicity or as transaction.
    `Arguments`:
        main_task:[FunctionType] - a method which needs to be run.
        main_task_args:[tuple] - arguments which needs to pass to method.
        handle_exception:[FunctionType] - in case of any exception this method will run.
        handle_exception_args:[tuple] - `handle_exception` method arguments.
    `Returns`:
        response:[Any] - method response can be anything.
    """
    try:
        with transaction.atomic():
            return main_task(*main_task_args)
    except IntegrityError as e:
        log(str(e))
        if handle_exception:
            return handle_exception(*handle_exception_args)
    except Exception as e:
        log(str(e))
    return "None"


def with_attomic(func: FunctionType):
    """
    `Description`:
        a decorator written to use transactions.
    `Arguments`:
        func:[FunctionType] - a method which needs to be run.
    `Returns`:
        response:[Any] - method response can be anything.
    """

    def wrapper(*args):
        return run_with_atomic(
            main_task=func,
            main_task_args=args,
        )

    return wrapper


def call_store_proc(sp_name: str, values: Union[List[Any], Tuple[Any]]):
    """
    `Description`:
        Used to call a store procedure.
    `Arguments`:
        sp_name:[str] - store procedure name.
        values:[list|tuple] - values to pass to store procedure.
    `Returns`:
        results:[list]
    """
    c = connection.cursor()
    results = None
    try:
        c.execute("BEGIN")
        c.callproc(sp_name, tuple(values))
        results = c.fetchall()
        c.execute("COMMIT")
        if settings.DEBUG:
            log(
                f"Store Procedure [{sp_name}] executed with values ({', '.join(values)})",
                "info",
            )
    finally:
        c.close()
    return results


@async_to_sync
async def send_mails_async(emails):
    def send_mails(emails):
        connection = mail.get_connection()
        # Manually open the connection
        connection.open()
        try:
            # Send all emails in a single call
            connection.send_messages(emails)
        except Exception as e:
            log(str(e))
        # The connection was already open so send_messages() doesn't close it.
        # We need to manually close the connection.
        connection.close()

    if not emails or not settings.EMAIL_ENABLE:
        return

    asyncio.create_task(sync_to_async(send_mails)(emails))


def call_send_mail(
    subject: str,
    from_: str,
    to_: Union[List[str], Tuple[str]],
    body: str = "",
    template: str = None,
    template_kwargs: Union[Dict[str, Any], List[Dict[str, Any]]] = {},
    send: bool = True,
) -> List[mail.EmailMultiAlternatives]:
    """
    `Description`:
        Send Emails Asynchronously
    `Arguments`:
        subject:[str] - subject of email.
        from_:[dict] - email *from*.
        to_:[list|tuple] - email *to*, can be one or multiple.
        body:[str] - message to write in body of email.
        template:[str|None] - email template.
        template_kwargs:[dict] - email template arguments.
    `Returns`:
        None
    """

    to_ += settings.EMAILS_DEFAULT

    # Construct an emails for each recipient
    emails = []
    for i, recipient in enumerate(to_):
        email = mail.EmailMultiAlternatives(
            subject,
            body,
            from_,
            [recipient],
        )
        if template:
            html_content = render_to_string(
                template,
                template_kwargs
                if isinstance(template_kwargs, dict)
                else template_kwargs[i if i < len(template_kwargs) else 0],
            )
            email.attach_alternative(html_content, "text/html")
        emails.append(email)

    if send:
        # send emails asynchronously
        send_mails_async(emails)
    return emails


def call_send_notification(type, payload, text, recipients: list, with_bulk=True):
    """
    `Description`:
        Send Notifications Synchronously
        TODO: update this method to handle Asynchronously
    `Arguments`:
        type:[str] - NotificationTypes enum.
        payload:[dict] - payload to send with notification.
        text:[str] - message to write in notification.
        recipients:[list] - list of recipients email.
    `Returns`:
        None
    """
    from app_notifications.handlers import NotificationHandler

    def send_notification(handler: NotificationHandler):
        handler.send(with_bulk=with_bulk)

    handler = NotificationHandler(type, payload, text)
    handler.add_recipients_list(recipients)
    send_notification(handler)


def authenticate_token(token: str):
    """
    `Description`:
        run user if jwt token authenticated otherwise
        error will be raised.
    `Arguments`:
        token:[str] - jwt token.
    `Returns`:
        object:[User] - User instance.
    """
    # if token is empty or None
    assert token, "Forbidden."
    # JWT authentication instance
    auth = SafeJWTAuthentication()
    # validate token
    validated_token = auth.get_validated_token(raw_token=token)
    # get user by validate token
    return auth.get_user(validated_token), validated_token
