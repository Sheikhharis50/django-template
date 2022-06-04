from django.db import models
import uuid

from .managers import NotificationRecipientManager


def notification_payload_default():
    return dict(id="")


class Notification(models.Model):
    """
    `notification` - to store app notifications.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(
        verbose_name="Notification Type",
        max_length=255,
        blank=False,
        null=True,
    )
    payload = models.JSONField(
        verbose_name="Notification Payload",
        default=notification_payload_default,
    )
    text = models.TextField(
        verbose_name="Notification Text",
        blank=True,
        null=True,
    )
    is_hidden = models.BooleanField(verbose_name="hidden", default=False)
    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)

    class Meta:
        db_table = "notification"
        verbose_name = "Notification"
        ordering = ["-created_at"]

    def __str__(self):
        return self.text


class NotificationRecipient(models.Model):
    """
    `notification_recipient` - app notification's recipients.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        to="app_accounts.User",
        on_delete=models.DO_NOTHING,
        verbose_name="user",
        db_column="user_id",
        related_name="notifications",
        blank=False,
        null=True,
    )
    notification = models.ForeignKey(
        to="app_notifications.Notification",
        on_delete=models.DO_NOTHING,
        verbose_name="notification",
        db_column="notification_id",
        related_name="recipients",
        blank=False,
        null=True,
    )
    seen_at = models.DateTimeField(
        verbose_name="seened at",
        null=True,
        blank=True,
    )

    objects = NotificationRecipientManager()

    class Meta:
        db_table = "notification_recipient"
        verbose_name = "Notification Recipient"
        ordering = ["-id"]

    def __str__(self):
        return self.user.full_name if self.user else None
