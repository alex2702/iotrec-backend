from django.contrib import admin

from iotrec_api.models import Thing
from training.models import ContextFactorValue, Sample, ContextFactor, TrainingUser, ReferenceThing


class ReferenceThingAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'indoorsLocation', 'categories', 'type', 'image']
    list_display = ['title', 'description', 'indoorsLocation']


admin.site.register(ReferenceThing, ReferenceThingAdmin)


class ContextFactorAdmin(admin.ModelAdmin):
    fields = ['title', 'display_title']
    list_display = ['display_title']


admin.site.register(ContextFactor, ContextFactorAdmin)


class ContextFactorValueAdmin(admin.ModelAdmin):
    fields = ['title', 'display_title', 'description', 'context_factor']
    list_display = ['display_title', 'context_factor']


admin.site.register(ContextFactorValue, ContextFactorValueAdmin)


class SampleAdmin(admin.ModelAdmin):
    fields = ['thing', 'context_factor', 'context_factor_value', 'value', 'user']
    list_display = ['thing', 'context_factor', 'context_factor_value', 'value']


admin.site.register(Sample, SampleAdmin)


class TrainingUserAdmin(admin.ModelAdmin):
    #fields = ['']
    list_display = ['identifier']


admin.site.register(TrainingUser, TrainingUserAdmin)
