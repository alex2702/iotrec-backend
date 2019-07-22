from django import forms

from iotrec_api.models import Venue


class VenueChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title