from django.db import models
from django.conf import settings

class Secret(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    label = models.CharField(max_length=32,
                             null=True,
                             blank=True,
                             help_text='Human readable label that can optionally be used for convenience',
                             )
    data = models.TextField(null=False,
                            blank=False,
                            )
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL)
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
