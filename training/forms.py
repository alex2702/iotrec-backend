import random

from django import forms
from .models import Sample, ReferenceThing, ContextFactor


class SampleForm(forms.Form):
    thing = forms.IntegerField(widget=forms.HiddenInput())

    context_factor_1 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_2 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_3 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_4 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_5 = forms.IntegerField(widget=forms.HiddenInput())

    context_factor_value_1 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_value_2 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_value_3 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_value_4 = forms.IntegerField(widget=forms.HiddenInput())
    context_factor_value_5 = forms.IntegerField(widget=forms.HiddenInput())

    CHOICES = [
        ('-1', 'negative effect'),
        ('0', 'no effect'),
        ('1', 'positive effect')
    ]

    value_1 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    value_2 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    value_3 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    value_4 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    value_5 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

    user = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Sample
        fields = ['thing',
                  'context_factor_1', 'context_factor_2', 'context_factor_3', 'context_factor_4', 'context_factor_5',
                  'context_factor_value_1', 'context_factor_value_2', 'context_factor_value_3', 'context_factor_value_4', 'context_factor_value_5',
                  'value_1', 'value_2', 'value_3', 'value_4', 'value_5',
                  'user']