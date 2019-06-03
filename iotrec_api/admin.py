from iotrec_api.models import Thing
from django.contrib import admin

class ThingAdmin(admin.ModelAdmin):
    fields = ['uuid', 'major_id', 'minor_id', 'title', 'description', 'image']
    list_display = ('title', 'uuid', 'major_id', 'minor_id')

admin.site.register(Thing, ThingAdmin)