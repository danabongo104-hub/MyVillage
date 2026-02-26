from django.db import models
from django.conf import settings


class FeedFilter(models.Model):
    """
    Stores per-user feed preferences so their sorting
    and filter choices persist between sessions.
    """
    SORT_BY_DATE = 'date'
    SORT_BY_POPULARITY = 'popularity'
    SORT_CHOICES = [
        (SORT_BY_DATE, 'Date'),
        (SORT_BY_POPULARITY, 'Popularity'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_filter'
    )
    sort_by = models.CharField(
        max_length=20,
        choices=SORT_CHOICES,
        default=SORT_BY_DATE
    )
    therapists_only = models.BooleanField(default=False)
    keyword_filter = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s feed preferences"