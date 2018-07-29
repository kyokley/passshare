import base64
import os

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

# Defaults
COUNTDOWN_DEFAULT = 14
SIZE_DEFAULT = 0
LABEL_MAX_LENGTH = 32
UNENCRYPTED_HASH_MAX_LENGTH = 64
FILENAME_MAX_LENGTH = 32
USERNAME_MAX_LENGTH = 32
SITE_MAX_LENGTH = 256

class Secret(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='%(class)s_related',
                                     )
    countdown = models.IntegerField(null=False,
                                    blank=False,
                                    default=COUNTDOWN_DEFAULT,
                                    choices=COUNTDOWN_CHOICES,
                                    )
    unencrypted_hash = models.CharField(max_length=UNENCRYPTED_HASH_MAX_LENGTH,
                                        null=False,
                                        blank=False)
    size = models.BigIntegerField(null=False,
                                  blank=False,
                                  default=SIZE_DEFAULT)
    date_created = models.DateField(auto_now_add=True)
    date_edited = models.DateField(auto_now=True)

    class Meta:
        abstract = True

    def new(self,
            owner,
            unencrypted_hash,
            countdown=COUNTDOWN_DEFAULT,
            size=SIZE_DEFAULT,
            ):
        self.owner = owner
        self.countdown = countdown
        self.unencrypted_hash = unencrypted_hash
        self.size = size

        self.save()

    def new_unencrypted(self,
                        owner,
                        label,
                        unencrypted_data='test_string',
                        countdown=COUNTDOWN_DEFAULT,
                        ):
        if isinstance(unencrypted_data, str):
            unencrypted_data = unencrypted_data.encode('utf-8')

        fake_data = base64.b64encode(unencrypted_data)
        size = len(fake_data)

        self.new(owner,
                 label,
                 fake_data,
                 countdown=countdown,
                 size=size)

class TextSecret(Secret):
    data = models.TextField(null=False, # base64 encoded encrypted data
                            blank=False,
                            )
    label = models.CharField(max_length=LABEL_MAX_LENGTH,
                             null=False,
                             blank=False,
                             help_text='Human readable label',
                             )

    class Meta:
        unique_together = ('owner', 'label')

    def new(self,
            owner,
            unencrypted_hash,
            label,
            data,
            countdown=COUNTDOWN_DEFAULT,
            ):
        if not label:
            raise Exception('Label must be defined and not empty')
        if not data:
            raise Exception('Data must be defined and not empty')

        self.label = label
        self.data = data

        super().new(owner,
                    unencrypted_hash,
                    countdown=countdown,
                    size=len(data),
                    )

class FileSecret(Secret):
    file_path = models.TextField(null=True, # location on the filesystem where encrypted data lives
                                 blank=True,
                                 )
    filename = models.CharField(max_length=FILENAME_MAX_LENGTH,
                                null=False,
                                blank=False,
                                help_text='Name of file being stored')

    class Meta:
        unique_together = ('owner', 'filename')

    def new(self,
            owner,
            unencrypted_hash,
            filename,
            raw_data,
            countdown=COUNTDOWN_DEFAULT,
            size=SIZE_DEFAULT,
            ):
        if not filename:
            raise Exception('Filename must be defined and not empty')
        if not raw_data:
            raise Exception('Data must be provided')

        self.filename = filename

        super().new(owner,
                    unencrypted_hash,
                    countdown=countdown,
                    size=size)

        self.file_path = self._get_local_file_path(owner)

        with open(self.file_path, 'wb') as f:
            f.write(raw_data)

        self.save()

    def _get_local_file_path(self, owner):
        # Create dir for new file
        owner_dir_path = os.path.join(settings.USER_FILE_DIR_ROOT, str(owner.id))
        os.makedirs(owner_dir_path, mode=0o750, exist_ok=True)
        return os.path.join(owner_dir_path, str(self.id))

class UPSecret(Secret):
    password = models.TextField(null=False, # base64 encoded encrypted data
                            blank=False,
                            )
    username = models.CharField(max_length=USERNAME_MAX_LENGTH,
                                null=False,
                                blank=False)
    label = models.CharField(max_length=LABEL_MAX_LENGTH,
                             null=False,
                             blank=False,
                             help_text='Human readable label',
                             )

    class Meta:
        unique_together = ('owner', 'label', 'username')

    def new(self,
            owner,
            unencrypted_hash,
            label,
            username,
            password,
            countdown=COUNTDOWN_DEFAULT,
            size=SIZE_DEFAULT,
            ):
        self.username = username
        self.password = password

        super().new(owner,
                    unencrypted_hash,
                    countdown=countdown,
                    size=size)
