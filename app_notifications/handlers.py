from .models import Notification, NotificationRecipient


class NotificationHandler:
    def __init__(self, type, payload, text) -> None:
        self._type = type
        self._payload = payload
        self._text = text
        self._recipients = []

    def send(self, with_bulk=True):
        notification = Notification.objects.create(
            type=self._type,
            payload=self._payload,
            text=self._text,
        )
        for recipient in self._recipients:
            recipient.notification = notification
            if not with_bulk:
                recipient.save()
        if with_bulk:
            NotificationRecipient.objects.bulk_create(self._recipients)

    def add_recipient(self, recipient):
        self._recipients.append(NotificationRecipient(user_id=recipient))

    def add_recipients_list(self, recipients):
        assert isinstance(
            recipients, (list, tuple)
        ), "`recipients` should be either tuple or list."
        for recipient in recipients:
            self.add_recipient(recipient)
