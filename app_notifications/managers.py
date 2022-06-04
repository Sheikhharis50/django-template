from django.db import models


class NotificationRecipientManager(models.Manager):
    def get_notifications(self, user, type=None, limit=None):
        filters = models.Q(notification__is_hidden=False, user=user)
        if type:
            filters &= models.Q(notification__type=type)

        qs = (
            self.select_related("notification")
            .filter(filters)
            .order_by("-notification__created_at")
        )
        if limit:
            return qs[:limit]
        return qs
