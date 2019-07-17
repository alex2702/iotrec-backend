from iotrec_api.models import IotRecUser, Thing, Venue
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django import forms


# source: https://stackoverflow.com/a/17496836
from iotrec_api.utils.venue import VenueChoiceField


class IotRecUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = IotRecUser


# source: https://stackoverflow.com/a/17496836
class IotRecUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = IotRecUser

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            IotRecUser.objects.get(username=username)
        except IotRecUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


# source: https://stackoverflow.com/a/17496836
class IotRecUserAdmin(UserAdmin):
    form = IotRecUserChangeForm
    add_form = IotRecUserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('extra_field1', 'extra_field2',)}),
    )


# source: https://stackoverflow.com/a/17496836
admin.site.register(IotRecUser, IotRecUserAdmin)


class ThingsInLine(admin.TabularInline):
    model = Thing
    extra = 0


class ThingAdmin(admin.ModelAdmin):
    fields = ['type', 'uuid', 'major_id', 'minor_id', 'venue']
    # fields = [field.name for field in Thing._meta.get_fields()]
    list_display = ('uuid', 'major_id', 'minor_id', 'venue')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'venue':
            return VenueChoiceField(queryset=Venue.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Thing, ThingAdmin)


class VenueAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'image']
    # fields = [field.name for field in Venue._meta.get_fields()]
    list_display = ('title', 'description', 'image')
    inlines = [
        ThingsInLine
    ]


admin.site.register(Venue, VenueAdmin)