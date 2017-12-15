from django import forms
from django.db import models    
from django.forms import ModelForm, TextInput, NumberInput, ModelMultipleChoiceField, Select, widgets
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from .models import Order, Address, Sale, Product

from django_countries.widgets import CountrySelectWidget
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries, Countries
# from phonenumber_field.formfields import PhoneNumberField

class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = [
            'addressee',
            'street',
            'apt',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'email'
        ]
        widgets = {
            'addressee': TextInput(attrs={'required': "true", "id": "recip", "class": "ad-field"}),
            'street': TextInput(attrs={'id': 'autocomplete', 'class': 'field ad-field','required': "true"}),
            'city': TextInput(attrs={'class': 'input-field col mods field ad-field', 'id': 'locality','required': "true"}),
            'state': TextInput(attrs={'class': 'input-field col mods field ad-field', 'id': 'administrative_area_level_1','required': "true"}),
            'zip_code': TextInput(attrs={'class': 'input-field col mods ad-field', 'id': 'postal_code','required': "true"}),
            'phone': TextInput(attrs={'class': 'input-field col mods ad-field', 'id': 'phone','required': "true"}),
            'email': TextInput(attrs={'class': 'input-field col mods ad-field', 'id': 'email','required': "true"}),
            'apt': TextInput(attrs={'class': 'input-field col mods', 'id': 'apt'}),
        }

class BillingAddressForm(forms.Form):
    name = forms.CharField(required=True,widget=forms.TextInput(attrs={"id": "billing-name", "class": "ad-field"}))
    address_line1 = forms.CharField(required=True,widget=forms.TextInput(attrs={"onFocus": "geolocate()", "id": "billing-street", "class": "ad-field"}))
    address_line2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-field col mods', 'id': 'billing-apt'}))
    address_city = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'input-field col mods field ad-field', 'id': 'billing-city','required': "true"}))
    address_state = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'input-field col mods field ad-field', 'id': 'billing-state','required': "true"}))
    address_zip = forms.IntegerField(required=True,widget=forms.TextInput(attrs={'class': 'input-field col mods ad-field', 'id': 'billing-zip','required': "true"}))
    address_country = LazyTypedChoiceField(choices=countries)


class SaleAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SaleAdminForm, self).__init__(*args, **kwargs)
        self.fields['sale_items'].label = 'Sale Items'
    class Meta:
        model = Sale
        fields = ('headline',)
    sale_items = ModelMultipleChoiceField(queryset=Product.objects.all())


class OunceWidget(widgets.TextInput):
    def render(self, name, value, attrs=None):
        return mark_safe("<span>{} oz.</span>".format(super(OunceWidget, self).render(name,value,attrs)))

class InchWidget(widgets.TextInput):
    def render(self, name, value, attrs=None):
        return mark_safe("<span>{} in.</span>".format(super(InchWidget, self).render(name,value,attrs)))

class ProductAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['weight'].widget = OunceWidget()
        self.fields['length'].widget = InchWidget()
        self.fields['width'].widget = InchWidget()
        self.fields['depth'].widget = InchWidget()

class PenAdminForm(ModelForm):
    class Meta:
        labels = {
            "country": "Country (optional)"
        }      