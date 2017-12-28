from django.contrib import admin
from . import models
# Register your models here.

class UserConfig(admin.ModelAdmin):
    def cs(self):
        field=self.model._meta.get_field

admin.site.register(models.UserInfo)