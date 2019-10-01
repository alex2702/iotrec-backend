from django.contrib import admin
from django.db.models import Count

from iotrec_api.models import Thing
from training.models import ContextFactorValue, Sample, ContextFactor, TrainingUser, ReferenceThing


class ReferenceThingAdmin(admin.ModelAdmin):
    readonly_fields = ['samples_count']
    fields = ['title', 'description', 'indoorsLocation', 'categories', 'type', 'image', 'active', 'samples_count']
    list_display = ['title', 'description', 'indoorsLocation', 'active', 'samples_count']

    def get_queryset(self, request):
        return ReferenceThing.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'


admin.site.register(ReferenceThing, ReferenceThingAdmin)


class ContextFactorAdmin(admin.ModelAdmin):
    readonly_fields = ['samples_count']
    fields = ['title', 'display_title', 'active', 'samples_count']
    list_display = ['display_title', 'active', 'samples_count']

    def get_queryset(self, request):
        return ContextFactor.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'


admin.site.register(ContextFactor, ContextFactorAdmin)


class ContextFactorValueAdmin(admin.ModelAdmin):
    readonly_fields = ['samples_count']
    fields = ['title', 'display_title', 'description', 'active', 'context_factor', 'samples_count']
    list_display = ['display_title', 'active', 'context_factor', 'samples_count']

    def get_queryset(self, request):
        return ContextFactorValue.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'


admin.site.register(ContextFactorValue, ContextFactorValueAdmin)


class SampleAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    fields = ['thing', 'context_factor', 'context_factor_value', 'value', 'user']
    list_display = ['created_at', 'thing', 'context_factor', 'context_factor_value', 'value', 'user']


admin.site.register(Sample, SampleAdmin)


class TrainingUserAdmin(admin.ModelAdmin):
    readonly_fields = ['identifier', 'created_at', 'updated_at']
    list_display = ['identifier']


admin.site.register(TrainingUser, TrainingUserAdmin)
