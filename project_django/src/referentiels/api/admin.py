# Core
from django.contrib import admin
# Local
from referentiels.api import models, forms
# Revsion
from reversion.admin import VersionAdmin
# Import Export
# from import_export.admin import ImportExportMixin, ImportExportModelAdmin
# from import_export import resources


# Register your models here.

@admin.register(models.CCI)
class CCIAdmin(VersionAdmin, admin.ModelAdmin):
    """ Vue de l'administration avec gestion des versions et import/export """
    resources_class = models.CCI
    change_list_template = 'admin/api/change_list.html'


@admin.register(models.CFE)
class CFEAdmin(VersionAdmin, admin.ModelAdmin):
    form = forms.CFEAdminForm


# admin.site.register(models.Continent)

#class ContinentResource(resources.ModelResource):
#    class Meta:
#        model = models.Continent


@admin.register(models.Continent)
class ContinentAdmin(VersionAdmin, admin.ModelAdmin):
    resource_class = models.Continent
    change_list_template = 'admin/api/change_list.html'


# admin.site.register(models.Pays)

#class PaysResource(resources.ModelResource):
#    class Meta:
#        model = models.Pays


@admin.register(models.Pays)
class PaysAdmin(VersionAdmin, admin.ModelAdmin):
    resource_class = models.Pays
    change_list_template = 'admin/api/change_list.html'


@admin.register(models.Region)
class RegionAdmin(VersionAdmin, admin.ModelAdmin):
    class Meta:
        model = models.Region


@admin.register(models.Departement)
class DepartementAdmin(VersionAdmin, admin.ModelAdmin):
    class Meta:
        model = models.Departement

class PersonnelAdmin(VersionAdmin, admin.ModelAdmin):
    class Meta:
        model = models.Personnel

admin.site.register(models.Personnel)
admin.site.register(models.CodePostal)
admin.site.register(models.Acheminement)
admin.site.register(models.Adresse)
admin.site.register(models.Personne)
admin.site.register(models.Responsabilite)
admin.site.register(models.Qualite)
