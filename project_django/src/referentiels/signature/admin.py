from django.contrib import admin
from reversion.admin import VersionAdmin
from referentiels.signature import models

# Register your models here.
# @admin.register(models.Signature)
class SignatureAdmin(VersionAdmin, admin.ModelAdmin):
    class Meta:
        model = models.Signature

admin.site.register(models.Signature)