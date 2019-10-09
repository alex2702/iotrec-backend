from django.db.models import Count
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin

from iotrec_api.models import User, Thing, Category, Recommendation, Feedback, Preference, IotRecSettings
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django import forms


# source: https://stackoverflow.com/a/17496836
# from iotrec_api.utils.venue import VenueChoiceField


class InlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        for form in self.forms:
            for field in form.changed_data:
                print (form.cleaned_data[field])


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
    #fields = ['category', 'value']
    #readonly_fields = ['id', 'created_at', 'updated_at']
    extra = 0
    formset = InlineFormset


admin.site.register(IotRecSettings)


# source: https://stackoverflow.com/a/17496836
class IotRecUserAdmin(UserAdmin):
    form = IotRecUserChangeForm
    add_form = IotRecUserCreationForm
    #fieldsets = UserAdmin.fieldsets + (
    #    (None, {'fields': ('preferences',)}),
    #)
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


class ThingAdmin(admin.ModelAdmin):
    fields = ['id', 'title', 'description', 'categories', 'type', 'uuid', 'major_id', 'minor_id', 'image', 'address',
              'location', 'created_at', 'updated_at']
    # fields = [field.name for field in Thing._meta.get_fields()]
    list_display = ('title', 'uuid', 'major_id', 'minor_id')
    ordering = ('-created_at',)

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
    fields = ['id', 'user', 'thing', 'score', 'invoke_rec', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'user', 'thing', 'score', 'invoke_rec')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at', 'score']


admin.site.register(Recommendation, RecommendationAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    fields = ['id', 'recommendation', 'value', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'recommendation', 'value')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Feedback, FeedbackAdmin)

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
