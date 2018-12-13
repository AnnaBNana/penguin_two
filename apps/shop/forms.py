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
            'addressee': TextInput(attrs={'required': "true", "id": "recip", "class": "address-field"}),
            'street': TextInput(attrs={'id': 'autocomplete', 'class': 'field address-field','required': "true"}),
            'city': TextInput(attrs={'class': 'input-field col mods field address-field', 'id': 'locality','required': "true"}),
            'state': TextInput(attrs={'class': 'input-field col mods field address-field', 'id': 'administrative_area_level_1','required': "true"}),
            'zip_code': TextInput(attrs={'class': 'input-field col mods address-field', 'id': 'postal_code','required': "true"}),
            'phone': TextInput(attrs={'class': 'input-field col mods address-field', 'id': 'phone','required': "true"}),
            'email': TextInput(attrs={'class': 'input-field col mods address-field', 'id': 'email','required': "true"}),
            'apt': TextInput(attrs={'class': 'input-field col mods', 'id': 'apt'}),
        }

class BillingAddressForm(forms.Form):
    name = forms.CharField(required=True,widget=forms.TextInput(attrs={"id": "billing-name", "class": "address-field"}))
    address_line1 = forms.CharField(required=True,widget=forms.TextInput(attrs={"onFocus": "geolocate()", "id": "billing-street", "class": "address-field"}))
    address_line2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-field col mods', 'id': 'billing-apt'}))
    address_city = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'input-field col mods field address-field', 'id': 'billing-city','required': "true"}))
    address_state = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'input-field col mods field address-field', 'id': 'billing-state','required': "true"}))
    address_zip = forms.IntegerField(required=True,widget=forms.TextInput(attrs={'class': 'input-field col mods address-field', 'id': 'billing-zip','required': "true"}))
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
    class Meta:
        labels = {
            "in_stock": "Number in Stock",
            "cost": "Purchase cost",

        }
    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['weight'].widget = OunceWidget()
        self.fields['length'].widget = InchWidget()
        self.fields['width'].widget = InchWidget()
        self.fields['depth'].widget = InchWidget()
    def clean(self):
        status = self.cleaned_data.get('status')
        in_stock = self.cleaned_data.get('in_stock')
        if in_stock > 0 and status != 'A':
            raise forms.ValidationError("If item status is sold, item 'number in stock' must be 0.")
        if in_stock < 1 and status != 'S':
            raise forms.ValidationError("If product 'number in stock' is 0, item must be marked sold.")


class PenAdminForm(ModelForm):
    class Meta:
        labels = {
            "country": "Country (optional)"
        }      
