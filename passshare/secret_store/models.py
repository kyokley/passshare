from django.db import models
from django.conf import settings

COUNTDOWN_CHOICES = (
        (1, 1),
        (7, 7),
        (14, 14),
        (30, 30),
        (60, 60),
        (90, 90),
        )
class Secret(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    label = models.CharField(max_length=32,
                             null=True,
                             blank=True,
                             help_text='Human readable label that can optionally be used for convenience',
                             )
    data = models.TextField(null=False, # base64 encoded encrypted data
                            blank=False,
                            )
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='%(class)s_related',
                                     )
    countdown = models.IntegerField(null=False,
                                    blank=False,
                                    default=14,
                                    choices=COUNTDOWN_CHOICES,
                                    )
    unencrypted_hash = models.CharField(max_length=64,
                                        null=False,
                                        blank=False)
    date_created = models.DateField(auto_now_add=True)
    date_edited = models.DateField(auto_now=True)

    class Meta:
        abstract = True

class TextSecret(Secret):
    pass

class FileSecret(Secret):
    filename = models.CharField(max_length=32,
                                null=False,
                                blank=False)

class UPSecret(Secret):
    username = models.CharField(max_length=32,
                                null=False,
                                blank=False)
