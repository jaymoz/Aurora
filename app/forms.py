from django import forms
from .models import *
from django.forms import CheckboxSelectMultiple, ModelForm
import django_filters
from django_filters import FilterSet
from django_filters import DateFilter
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterUserForm(UserCreationForm):
	username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
		'placeholder':'Username'
		}))
	email = forms.EmailField(widget=forms.EmailInput(attrs={
		'placeholder':'E-mail'
		}))

	password1 = forms.CharField(widget=forms.PasswordInput(attrs={
		'placeholder':'Password'
		}))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={
		'placeholder':'Confirm Password'
		}))

	class Meta:
		model = User
		fields = ("username","email","password1","password2")


class CheckoutForm(forms.Form):
	full_name = forms.CharField(required=True)
	city = forms.CharField(required=True)
	house_address = forms.CharField(required=True)
	country = forms.CharField(required=True)
	postal_code = forms.CharField(required=True)
	phone = forms.CharField(required=True)
	order_notes = forms.CharField(required=True)
	set_default_delivery = forms.BooleanField(required=False)
	use_default_delivery = forms.BooleanField(required=False)

	# phone = forms.IntegerField(required=False,validators=[RegexValidator(regex=r'^(\+?7|8)\d{10}$', message='Phone number must be entered in the format: (+7|8) 960 xxx-xx-xx ' )])