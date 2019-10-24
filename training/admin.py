from django.contrib import admin
from django.db.models import Count

from training.models import ContextFactorValue, Sample, ContextFactor, TrainingUser, ReferenceThing, ContextBaseline, \
    ThingBaseline


class ReferenceThingAdmin(admin.ModelAdmin):
    readonly_fields = ['samples_count']
    fields = ['title', 'description', 'indoorsLocation', 'categories', 'type', 'image', 'active', 'samples_count']
    list_display = ['title', 'description', 'indoorsLocation', 'active', 'samples_count']
    list_filter = ['active', 'indoorsLocation']

    class Media:
        js = ('js/ref_thing_admin.js',)
        css = {
            'all': ('css/ref_thing_admin.css',)
        }

    def activate(self, request, queryset):
        queryset.update(active=True)

    def deactivate(self, request, queryset):
        queryset.update(active=False)

    activate.short_description = "Mark selected thing as active"
    deactivate.short_description = "Mark selected thing as inactive"

    def get_queryset(self, request):
        return ReferenceThing.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'

    actions = [activate, deactivate]


admin.site.register(ReferenceThing, ReferenceThingAdmin)


class ContextFactorAdmin(admin.ModelAdmin):
    readonly_fields = ['title', 'samples_count']
    fields = ['title', 'display_title', 'active', 'samples_count']
    list_display = ['display_title', 'active', 'samples_count']
    list_filter = ['active']

    def activate(self, request, queryset):
        queryset.update(active=True)

    def deactivate(self, request, queryset):
        queryset.update(active=False)

    activate.short_description = "Mark selected context factors as active"
    deactivate.short_description = "Mark selected context factors as inactive"

    def get_queryset(self, request):
        return ContextFactor.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'

    actions = [activate, deactivate]


admin.site.register(ContextFactor, ContextFactorAdmin)


class ContextFactorValueAdmin(admin.ModelAdmin):
    readonly_fields = ['title', 'context_factor_active', 'samples_count']
    fields = ['title', 'display_title', 'description', 'active', 'context_factor', 'context_factor_active',
              'samples_count']
    list_display = ['display_title', 'active', 'context_factor_active', 'context_factor', 'samples_count']
    list_filter = ['active']

    def activate(self, request, queryset):
        queryset.update(active=True)

    def deactivate(self, request, queryset):
        queryset.update(active=False)

    activate.short_description = "Mark selected context factor values as active"
    deactivate.short_description = "Mark selected context factor values as inactive"

    def get_queryset(self, request):
        return ContextFactorValue.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    def context_factor_active(self, obj):
        return obj.context_factor.active

    context_factor_active.boolean = True

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'
    context_factor_active.short_description = 'Context Factor Active'
    context_factor_active.admin_order_field = 'context_factor__active'

    actions = [activate, deactivate]


admin.site.register(ContextFactorValue, ContextFactorValueAdmin)


class SampleAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    fields = ['thing', 'context_factor', 'context_factor_value', 'value', 'user']
    list_display = ['created_at', 'thing', 'context_factor', 'context_factor_value', 'value', 'user']
    list_filter = ['value', 'thing', 'context_factor', 'context_factor_value', 'user']


admin.site.register(Sample, SampleAdmin)


class TrainingUserAdmin(admin.ModelAdmin):
    readonly_fields = ['identifier', 'created_at', 'updated_at', 'samples_count']
    fields = ['identifier', 'samples_count', 'created_at', 'updated_at']
    list_display = ['created_at', 'identifier', 'samples_count']

    def get_queryset(self, request):
        return TrainingUser.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'


admin.site.register(TrainingUser, TrainingUserAdmin)


class ContextBaselineAdmin(admin.ModelAdmin):
    readonly_fields = ['reference_thing', 'context_factor', 'context_factor_value', 'value', 'updated_at']
    fields = ['reference_thing', 'context_factor', 'context_factor_value', 'value', 'updated_at']
    list_display = ['updated_at', 'reference_thing', 'context_factor', 'context_factor_value', 'value']


admin.site.register(ContextBaseline, ContextBaselineAdmin)


class ThingBaselineAdmin(admin.ModelAdmin):
    readonly_fields = ['reference_thing', 'value', 'updated_at']
    fields = ['reference_thing', 'value', 'updated_at']
    list_display = ['updated_at', 'reference_thing', 'value']


admin.site.register(ThingBaseline, ThingBaselineAdmin)
