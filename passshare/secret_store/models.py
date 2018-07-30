import base64
import os
import hashlib

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

DISPLAY_TRUNCATE_LENGTH = 32

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

    @property
    def display_hash(self):
        return (self.unencrypted_hash[:DISPLAY_TRUNCATE_LENGTH] + '...'
                    if len(self.unencrypted_hash) > DISPLAY_TRUNCATE_LENGTH
                    else self.unencrypted_hash)

    @classmethod
    def new(cls,
            owner,
            unencrypted_hash,
            countdown=COUNTDOWN_DEFAULT,
            size=SIZE_DEFAULT,
            ):
        instance = cls()

        instance.owner = owner
        instance.countdown = countdown
        instance.unencrypted_hash = unencrypted_hash
        instance.size = size

        return instance

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

    def __str__(self):
        return 'id: {id} O: {owner} L: {label} H: {hash}'.format(id=getattr(self, 'id', None),
                                                                 owner=self.owner.username,
                                                                 label=self.label,
                                                                 hash=self.display_hash,
                                                                 )

    @property
    def display_data(self):
        return (self.data[:DISPLAY_TRUNCATE_LENGTH] + '...'
                    if len(self.data) > DISPLAY_TRUNCATE_LENGTH
                    else self.data)

    @classmethod
    def new(cls,
            owner,
            label,
            data,
            unencrypted_hash,
            countdown=COUNTDOWN_DEFAULT,
            ):
        if not label:
            raise Exception('Label must be defined and not empty')
        if not data:
            raise Exception('Data must be defined and not empty')

        instance = super().new(owner,
                               unencrypted_hash,
                               countdown=countdown,
                               size=len(data),
                               )
        instance.label = label
        instance.data = data
        instance.save()

        return instance

    @classmethod
    def new_from_unencrypted(cls,
                             owner,
                             label,
                             unencrypted_data='test_string',
                             countdown=COUNTDOWN_DEFAULT,
                             ):
        if isinstance(unencrypted_data, str):
            unencrypted_data = unencrypted_data.encode('utf-8')

        unencrypted_hash = hashlib.sha256(unencrypted_data).hexdigest()
        fake_data = base64.b64encode(unencrypted_data).decode('utf-8')

        instance = cls.new(owner,
                           label,
                           fake_data,
                           unencrypted_hash,
                           countdown=countdown,
                           )
        return instance


class FileSecret(Secret):
    file_path = models.TextField(null=True, # location on the filesystem where encrypted data lives
                                 blank=True,
                                 )
    filename = models.CharField(max_length=FILENAME_MAX_LENGTH,
                                null=False,
                                blank=False,
                                help_text='Name of file being stored')
    _display_data = models.CharField(max_length=DISPLAY_TRUNCATE_LENGTH,
                                     null=True,
                                     blank=True)

    class Meta:
        unique_together = ('owner', 'filename')

    @property
    def display_data(self):
        if len(self._display_data) >= DISPLAY_TRUNCATE_LENGTH:
            return self._display_data + '...'
        else:
            return self._display_data

    def __str__(self):
        return 'id: {id} O: {owner} F: {filename} P: {path} H: {hash}'.format(id=getattr(self, 'id', None),
                                                                              owner=self.owner.username,
                                                                              filename=self.filename,
                                                                              path=self.file_path,
                                                                              hash=self.display_hash,
                                                                              )

    @classmethod
    def new(cls,
            owner,
            unencrypted_hash,
            filename,
            raw_data,
            countdown=COUNTDOWN_DEFAULT,
            ):
        if not filename:
            raise Exception('Filename must be defined and not empty')
        if not raw_data:
            raise Exception('Data must be provided')


        instance = super().new(owner,
                               unencrypted_hash,
                               countdown=countdown,
                               size=len(raw_data))

        instance.filename = filename
        instance.save()

        instance.file_path = instance._get_local_file_path(owner)

        with open(instance.file_path, 'wb') as f:
            f.write(raw_data)

        instance._display_data = (raw_data[:DISPLAY_TRUNCATE_LENGTH].decode('utf-8') if len(raw_data) > DISPLAY_TRUNCATE_LENGTH
                                     else raw_data.decode('utf-8'))

        instance.save()
        return instance

    def _get_local_file_path(self, owner):
        # Create dir for new file
        owner_dir_path = os.path.join(settings.USER_FILE_DIR_ROOT, str(owner.id))
        os.makedirs(owner_dir_path, mode=0o750, exist_ok=True)
        return os.path.join(owner_dir_path, str(self.id))

    @classmethod
    def new_from_unencrypted(cls,
                             owner,
                             unencrypted_file_path,
                             countdown=COUNTDOWN_DEFAULT,
                             ):
        if not unencrypted_file_path or not os.path.exists(unencrypted_file_path):
            raise Exception('Given unencrypted_file_path does not exist')

        with open(unencrypted_file_path, 'rb') as f:
            data = f.read()

        unencrypted_hash = hashlib.sha256(data).hexdigest()
        fake_data = base64.b64encode(data)

        instance = cls.new(owner,
                           unencrypted_hash,
                           os.path.basename(unencrypted_file_path),
                           fake_data,
                           countdown=countdown,
                           )
        return instance

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

    def __str__(self):
        return 'id: {id} O: {owner} L: {label} U: {username} H: {hash}'.format(id=getattr(self, 'id', None),
                                                                               owner=self.owner.username,
                                                                               label=self.label,
                                                                               username=self.username,
                                                                               hash=self.display_hash,
                                                                               )
    @property
    def display_password(self):
        return (self.password[:DISPLAY_TRUNCATE_LENGTH] + '...'
                    if len(self.password) > DISPLAY_TRUNCATE_LENGTH
                    else self.password)

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
