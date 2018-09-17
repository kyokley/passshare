from django.contrib import admin
from passshare.secret_store.models import (TextSecret,
                                           FileSecret,
                                           UPSecret,
                                           )

# Register your models here.
admin.site.register(TextSecret)
admin.site.register(FileSecret)
admin.site.register(UPSecret)
