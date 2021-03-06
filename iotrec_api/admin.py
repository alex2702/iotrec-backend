from django.contrib.admin.actions import delete_selected
from django.forms import Select, SelectMultiple
from django.utils.encoding import smart_text
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from mptt.admin import MPTTModelAdmin
from iotrec_api.models import User, Thing, Category, Recommendation, Feedback, Preference, IotRecSettings, Rating, \
    Stay, SimilarityReference, Context
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django import forms
from iotrec_api.utils import similarity_reference
from iotrec_api.utils.category import calc_items_in_cat_list

# display seconds in admin
from django.conf.locale.en import formats as en_formats
en_formats.DATETIME_FORMAT = "d-m-Y H:i:s"


class InlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        for form in self.forms:
            for field in form.changed_data:
                print(form.cleaned_data[field])


# source: https://stackoverflow.com/a/17496836
class IotRecUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


# source: https://stackoverflow.com/a/17496836
class IotRecUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class PreferencesInLine(admin.TabularInline):
    model = Preference
    extra = 0
    formset = InlineFormset


class IotRecSettingsAdmin(admin.ModelAdmin):
    fields = ['evaluation_mode', 'training_active', 'recommendation_threshold', 'nr_of_reference_things_per_thing',
              'category_weight', 'locality_weight', 'prediction_weight', 'context_weight']
    list_display = ('pk', 'evaluation_mode', 'training_active', 'recommendation_threshold',
                    'nr_of_reference_things_per_thing', 'category_weight', 'locality_weight', 'prediction_weight',
                    'context_weight')

    def get_readonly_fields(self, request, obj=None):
        return ['locality_weight', 'context_weight']


admin.site.register(IotRecSettings, IotRecSettingsAdmin)


# source: https://stackoverflow.com/a/17496836
class IotRecUserAdmin(UserAdmin):
    form = IotRecUserChangeForm
    add_form = IotRecUserCreationForm
    inlines = [PreferencesInLine]
    list_display = UserAdmin.list_display + ('preferences_selected',)

    # custom calculated field to get the number of preferences per user in the list
    def preferences_selected(self, obj):
        return obj.preferences.count()

    preferences_selected.short_description = 'Preferences Selected'
    preferences_selected.admin_order_field = 'preferences_selected'


admin.site.register(User, IotRecUserAdmin)


class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'text_id', 'nr_of_items_recursive', 'things_assigned', 'ref_things_assigned',
                    'user_prefs_positive', 'user_prefs_negative', 'is_alias', 'get_alias_owner_full')

    def get_readonly_fields(self, request, obj=None):
        return ['nr_of_items_recursive']

    def get_queryset(self, request):
        return Category.objects.exclude(text_id="Root")

    def get_alias_owner_full(self, obj):
        if obj.alias_owner is not None:
            ancestors = obj.alias_owner.get_ancestors(ascending=False, include_self=True)
            output_string = ""
            for a in ancestors:
                output_string += '/' + a.name
            return output_string

    # number of things in a category
    def things_assigned(self, obj):
        return obj.thing_set.count()

    things_assigned.short_description = 'Things Assigned'
    things_assigned.admin_order_field = 'things_assigned'

    # number of reference things in a category
    def ref_things_assigned(self, obj):
        return obj.referencething_set.count()

    ref_things_assigned.short_description = 'Reference Things Assigned'
    ref_things_assigned.admin_order_field = 'ref_things_assigned'

    # number of users that like this category
    def user_prefs_positive(self, obj):
        return obj.preferences.filter(value=1).count()

    user_prefs_positive.short_description = 'User Prefs +'
    user_prefs_positive.admin_order_field = 'user_prefs_positive'

    # number of users that dislike this category
    def user_prefs_negative(self, obj):
        return obj.preferences.filter(value=-1).count()

    user_prefs_negative.short_description = 'User Prefs -'
    user_prefs_negative.admin_order_field = 'user_prefs_negative'


admin.site.register(Category, CategoryAdmin)


class SelectMultipleWithDisabled(SelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if attrs is None:
            attrs = {}
        if label is None:
            label = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if 'selected' in label and label['selected'] is True:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)
        if 'disabled' in label and label['disabled'] is True:
            option_attrs['disabled'] = 'disabled'
        if 'label' in label:
            option['label'] = label['label']
        if 'selected' in label:
            option['selected'] = label['selected']
        option['attrs'] = option_attrs

        return option


class ThingAdminForm(forms.ModelForm):
    class Meta:
        model = Thing
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.level_indicator = kwargs.pop('level_indicator', u'  ')

        super(ThingAdminForm, self).__init__(*args, **kwargs)

        queryset = Category.objects.all()
        mptt_opts = queryset.model._mptt_meta
        queryset = queryset.order_by(mptt_opts.tree_id_attr, mptt_opts.left_attr)

        choices = []
        for item in queryset:
            level = getattr(item, item._mptt_meta.level_attr)
            value = item.text_id
            label = mark_safe(conditional_escape(self.level_indicator) * level + smart_text(item.name))
            if item.is_leaf_node():
                choices.append(
                    (value, {'selected': item in self.instance.categories.all(), 'label': label, 'disabled': False}))
            else:
                choices.append(
                    (value, {'selected': item in self.instance.categories.all(), 'label': label, 'disabled': True}))

        self.fields['categories'] = forms.ChoiceField(choices=choices, widget=SelectMultipleWithDisabled)


class BulkDeleteMixin(object):
    class SafeDeleteQuerysetWrapper(object):
        def __init__(self, wrapped_queryset):
            self.wrapped_queryset = wrapped_queryset

        def _safe_delete(self):
            for obj in self.wrapped_queryset:
                categories = set(obj.categories.all())
                obj.delete()
                calc_items_in_cat_list(categories)

        def __getattr__(self, attr):
            if attr == 'delete':
                return self._safe_delete
            else:
                return getattr(self.wrapped_queryset, attr, None)

        def __iter__(self):
            for obj in self.wrapped_queryset:
                yield obj

        def __getitem__(self, index):
            return self.wrapped_queryset[index]

        def __len__(self):
            return len(self.wrapped_queryset)

    def get_actions(self, request):
        actions = getattr(super(BulkDeleteMixin, self), "get_actions")(request)
        actions['delete_selected'] = (BulkDeleteMixin.action_safe_bulk_delete, 'delete_selected', ugettext_lazy("Delete selected %(verbose_name_plural)s"))
        return actions

    def action_safe_bulk_delete(self, request, queryset):
        wrapped_queryset = BulkDeleteMixin.SafeDeleteQuerysetWrapper(queryset)
        return delete_selected(self, request, wrapped_queryset)


class ThingAdmin(BulkDeleteMixin, admin.ModelAdmin):
    fields = ['id', 'title', 'description', 'categories', 'type', 'ibeacon_uuid', 'ibeacon_major_id',
              'ibeacon_minor_id', 'eddystone_namespace_id', 'eddystone_instance_id', 'scenario', 'image',
              'indoorsLocation', 'address', 'location', 'created_at', 'updated_at']
    list_display = ('id', 'title', 'type', 'scenario', 'ibeacon_uuid', 'ibeacon_major_id', 'ibeacon_minor_id',
                    'eddystone_namespace_id', 'eddystone_instance_id', 'indoorsLocation', 'categories_assigned')
    ordering = ('-created_at',)

    # load custom CSS and JS for more comfortable category selection
    class Media:
        js = ('js/thing_admin.js',)
        css = {
            'all': ('css/thing_admin.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']

    # store old/previous categories and find new categories
    # then re-calculate the nr of items per category (for the changed one)
    def save_related(self, request, form, formsets, change):
        old_categories = set(form.instance.categories.all())
        super(ThingAdmin, self).save_related(request, form, formsets, change)
        new_categories = set(form.instance.categories.all())
        calc_items_in_cat_list((old_categories | new_categories))
        similarity_reference.calculate_similarity_references_per_thing(form.instance)

    def delete_model(self, request, obj):
        categories = set(obj.categories.all())
        super(ThingAdmin, self).delete_model(self, obj)
        calc_items_in_cat_list(categories)

    # add categories counter to list
    def categories_assigned(self, obj):
        return obj.categories.count()

    categories_assigned.short_description = 'Categories Assigned'
    categories_assigned.admin_order_field = 'categories_assigned'


admin.site.register(Thing, ThingAdmin)


class RecommendationAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'thing', 'context', 'experiment', 'score', 'preference_score', 'context_score',
              'invoke_rec', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'user', 'thing', 'score', 'preference_score', 'context_score', 'experiment',
                    'invoke_rec')
    ordering = ('-created_at',)
    list_filter = ['user', 'thing', 'experiment', 'created_at', 'invoke_rec']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at', 'score', 'preference_score', 'context_score', 'invoke_rec']


admin.site.register(Recommendation, RecommendationAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    fields = ['id', 'recommendation', 'value', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'recommendation', 'value')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Feedback, FeedbackAdmin)


class RatingAdmin(admin.ModelAdmin):
    fields = ['id', 'recommendation', 'value', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'recommendation', 'value')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Rating, RatingAdmin)


class PreferenceAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'category', 'value', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'user', 'category', 'value')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Preference, PreferenceAdmin)


class SimilarityReferenceAdmin(admin.ModelAdmin):
    fields = ['id', 'reference_thing', 'thing', 'similarity', 'created_at', 'updated_at']
    list_display = ('id', 'reference_thing', 'thing', 'similarity')

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(SimilarityReference, SimilarityReferenceAdmin)


class StayAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'thing', 'start', 'last_checkin', 'end', 'experiment', 'created_at', 'updated_at']
    list_display = ('id', 'user', 'thing', 'start', 'last_checkin', 'end')
    list_filter = ['user', 'thing', 'experiment', 'created_at']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Stay, StayAdmin)


class ContextAdmin(admin.ModelAdmin):
    fields = ['id', 'weather', 'temperature_raw', 'temperature', 'length_of_trip_raw', 'length_of_trip', 'crowdedness',
              'time_of_day', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'weather', 'temperature', 'length_of_trip', 'crowdedness', 'time_of_day')
    list_filter = ['created_at', 'recommendation__user']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Context, ContextAdmin)



