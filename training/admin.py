from django.contrib import admin
from django.db.models import Count

from training.models import ContextFactorValue, Sample, ContextFactor, TrainingUser, ReferenceThing, ContextBaseline, \
    ThingBaseline


class ReferenceThingAdmin(admin.ModelAdmin):
    readonly_fields = ['samples_count']
    fields = ['title', 'description', 'indoorsLocation', 'categories', 'type', 'image', 'active', 'samples_count']
    list_display = ['title', 'description', 'indoorsLocation', 'active', 'samples_count', 'categories_assigned']
    list_filter = ['active', 'indoorsLocation']

    class Media:
        js = ('js/ref_thing_admin.js',)
        css = {
            'all': ('css/ref_thing_admin.css',)
        }

    # custom list actions to batch-activate and -deactive reference things
    def activate(self, request, queryset):
        queryset.update(active=True)

    def deactivate(self, request, queryset):
        queryset.update(active=False)

    activate.short_description = "Mark selected thing as active"
    deactivate.short_description = "Mark selected thing as inactive"

    def get_queryset(self, request):
        return ReferenceThing.objects.annotate(samples_count=Count('sample'))

    # calculated field to show number of training samples per reference thing
    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'

    # calculated field to show number of categories per reference thing
    def categories_assigned(self, obj):
        return obj.categories.count()

    categories_assigned.short_description = 'Categories Assigned'
    categories_assigned.admin_order_field = 'categories_assigned'

    actions = [activate, deactivate]


admin.site.register(ReferenceThing, ReferenceThingAdmin)


class ContextFactorAdmin(admin.ModelAdmin):
    readonly_fields = ['title', 'samples_count']
    fields = ['title', 'display_title', 'active_in_training', 'active_in_prediction', 'samples_count']
    list_display = ['display_title', 'active_in_training', 'active_in_prediction', 'samples_count']
    list_filter = ['active_in_training', 'active_in_prediction']

    # custom list actions to batch-activate and -deactive context factors for training and evaluation
    def activate_in_training(self, request, queryset):
        queryset.update(active_in_training=True)

    def deactivate_in_training(self, request, queryset):
        queryset.update(active_in_training=False)

    def activate_in_prediction(self, request, queryset):
        queryset.update(active_in_prediction=True)

    def deactivate_in_prediction(self, request, queryset):
        queryset.update(active_in_prediction=False)

    activate_in_training.short_description = "Mark selected context factors as active for training"
    deactivate_in_training.short_description = "Mark selected context factors as inactive for training"
    activate_in_prediction.short_description = "Mark selected context factors as active for prediction"
    deactivate_in_prediction.short_description = "Mark selected context factors as inactive for prediction"

    def get_queryset(self, request):
        return ContextFactor.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'

    actions = [activate_in_training, deactivate_in_training, activate_in_prediction, deactivate_in_prediction]


admin.site.register(ContextFactor, ContextFactorAdmin)


class ContextFactorValueAdmin(admin.ModelAdmin):
    readonly_fields = ['title', 'context_factor_active_training', 'context_factor_active_prediction', 'samples_count']
    fields = ['title', 'display_title', 'description', 'active_in_training', 'active_in_prediction', 'context_factor',
              'context_factor_active_training', 'context_factor_active_prediction', 'samples_count']
    list_display = ['display_title', 'active_in_training', 'active_in_prediction', 'context_factor_active_training',
                    'context_factor_active_prediction', 'context_factor', 'samples_count']
    list_filter = ['active_in_training', 'active_in_prediction']

    def activate_training(self, request, queryset):
        queryset.update(active_in_training=True)

    def deactivate_training(self, request, queryset):
        queryset.update(active_in_training=False)

    def activate_prediction(self, request, queryset):
        queryset.update(active_in_prediction=True)

    def deactivate_prediction(self, request, queryset):
        queryset.update(active_in_prediction=False)

    activate_training.short_description = "Mark selected context factor values as active for training"
    deactivate_training.short_description = "Mark selected context factor values as inactive for training"
    activate_prediction.short_description = "Mark selected context factor values as active for prediction"
    deactivate_prediction.short_description = "Mark selected context factor values as inactive for prediction"

    def get_queryset(self, request):
        return ContextFactorValue.objects.annotate(samples_count=Count('sample'))

    def samples_count(self, obj):
        return obj.samples_count

    def context_factor_active_training(self, obj):
        return obj.context_factor.active_in_training

    def context_factor_active_prediction(self, obj):
        return obj.context_factor.active_in_prediction

    context_factor_active_training.boolean = True
    context_factor_active_prediction.boolean = True

    samples_count.short_description = 'Samples Count'
    samples_count.admin_order_field = 'samples_count'
    context_factor_active_training.short_description = 'Context Factor Active (Training)'
    context_factor_active_training.admin_order_field = 'context_factor__active_training'
    context_factor_active_prediction.short_description = 'Context Factor Active (Prediction)'
    context_factor_active_prediction.admin_order_field = 'context_factor__active_prediction'

    actions = [activate_training, deactivate_training, activate_prediction, deactivate_prediction]


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
