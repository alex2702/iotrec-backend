import pdb

from django.db.models import Count
from django.forms import Select, SelectMultiple
from django.utils.encoding import smart_text
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from jwt.utils import force_unicode
from mptt.admin import MPTTModelAdmin

from iotrec_api.models import User, Thing, Category, Recommendation, Feedback, Preference, IotRecSettings, Rating, Stay, \
    SimilarityReference, Context, AnalyticsEvent
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django import forms


# source: https://stackoverflow.com/a/17496836
# from iotrec_api.utils.venue import VenueChoiceField

# display seconds in admin
from django.conf.locale.en import formats as en_formats
en_formats.DATETIME_FORMAT = "d-m-Y H:i:s"

class InlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        for form in self.forms:
            for field in form.changed_data:
                print(form.cleaned_data[field])


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
    # fields = ['category', 'value']
    # readonly_fields = ['id', 'created_at', 'updated_at']
    extra = 0
    formset = InlineFormset


class IotRecSettingsAdmin(admin.ModelAdmin):
    fields = ['recommendation_threshold', 'nr_of_reference_things_per_thing', 'category_weight', 'locality_weight', 'prediction_weight', 'context_weight']
    list_display = ('pk', 'recommendation_threshold', 'nr_of_reference_things_per_thing', 'category_weight', 'locality_weight', 'prediction_weight', 'context_weight')

    def get_readonly_fields(self, request, obj=None):
        return ['locality_weight', 'context_weight']


admin.site.register(IotRecSettings, IotRecSettingsAdmin)


# source: https://stackoverflow.com/a/17496836
class IotRecUserAdmin(UserAdmin):
    form = IotRecUserChangeForm
    add_form = IotRecUserCreationForm
    # fieldsets = UserAdmin.fieldsets + (
    #    (None, {'fields': ('preferences',)}),
    # )
    inlines = [PreferencesInLine]


# source: https://stackoverflow.com/a/17496836
admin.site.register(User, IotRecUserAdmin)

"""
class ThingsInLine(admin.TabularInline):
    model = Thing
    extra = 0
"""


# class CategoriesInLine(admin.TabularInline):
#    model = Thing.categories.through
#    extra = 0


# class CategoryAdmin(admin.ModelAdmin):
#    fields = ['name', 'parent_category']
#    list_display = ['name', 'parent_category']


# admin.site.register(Category, CategoryAdmin)

class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'text_id', 'is_alias', 'get_alias_owner_full')

    def get_queryset(self, request):
        return Category.objects.exclude(text_id="Root")

    def get_alias_owner_full(self, obj):
        if obj.alias_owner is not None:
            ancestors = obj.alias_owner.get_ancestors(ascending=False, include_self=True)
            output_string = ""
            for a in ancestors:
                output_string += '/' + a.name
            return output_string


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
        # self.fields['categories'] = forms.ModelChoiceField(queryset=Category.objects.all(), widget=SelectMultipleWithDisabled)

    def clean_categories(self):
        print("clean_categories")
        print(self.__dict__)
        data = self.cleaned_data.get('categories', '')
        print(data)
        return data

    def clean(self):
        pdb.set_trace()
        print("clean")
        print(self.data)
        data = dict(self.data)
        string_categories = data['categories']
        for i in range(len(string_categories)):
            print(string_categories[i])

        super(ThingAdminForm, self).clean()

    def save(self, commit=True):
        self.full_clean()
        print("save")
        pdb.set_trace()
        instance = super().save(commit=False)
        # categories = self.cleaned_data['categories']
        # instance.publication = Publication.objects.get(pk=pub)
        instance.save(commit)
        return instance


class ThingAdmin(admin.ModelAdmin):
    fields = ['id', 'title', 'description', 'categories', 'type', 'ibeacon_uuid', 'ibeacon_major_id',
              'ibeacon_minor_id', 'eddystone_namespace_id', 'eddystone_instance_id', 'image',
              'indoorsLocation', 'address', 'location', 'created_at', 'updated_at']
    # fields = [field.name for field in Thing._meta.get_fields()]
    list_display = ('title', 'ibeacon_uuid', 'ibeacon_major_id', 'ibeacon_minor_id', 'eddystone_namespace_id',
                    'eddystone_instance_id')
    ordering = ('-created_at',)
    #form = ThingAdminForm

    class Media:
        js = ('js/thing_admin.js',)
        css = {
            'all': ('css/thing_admin.css',)
        }

    # inlines = [
    #    CategoriesInLine
    # ]

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']

    """"
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'venue':
            return VenueChoiceField(queryset=Venue.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    """


admin.site.register(Thing, ThingAdmin)

"""
class VenueAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'image']
    # fields = [field.name for field in Venue._meta.get_fields()]
    list_display = ('title', 'description', 'image')
    inlines = [
        ThingsInLine
    ]


admin.site.register(Venue, VenueAdmin)
"""


class RecommendationAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'thing', 'context', 'score', 'invoke_rec', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'user', 'thing', 'score', 'invoke_rec')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at', 'score', 'invoke_rec']


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


'''
class ThingsInLine(admin.TabularInline):
    model = Thing
    extra = 0


class CategoriesInLine(admin.TabularInline):
    model = Thing
    extra = 0
'''


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
    fields = ['id', 'user', 'thing', 'start', 'last_checkin', 'end', 'created_at', 'updated_at']
    list_display = ('id', 'user', 'thing', 'start', 'last_checkin', 'end')

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Stay, StayAdmin)


class ContextAdmin(admin.ModelAdmin):
    fields = ['id', 'weather', 'temperature_raw', 'temperature', 'length_of_trip_raw', 'length_of_trip', 'crowdedness', 'time_of_day', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'weather', 'temperature', 'length_of_trip', 'crowdedness', 'time_of_day')

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Context, ContextAdmin)


class AnalyticsEventAdmin(admin.ModelAdmin):
    fields = ['id', 'type', 'user', 'thing', 'recommendation', 'value', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'type', 'user', 'thing', 'recommendation', 'value')

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(AnalyticsEvent, AnalyticsEventAdmin)
