"""
Definition of forms.
"""


from django.contrib.auth.forms import AuthenticationForm
from django.forms import formsets
from django.forms.fields import IntegerField
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control input-border-bottom',
                                   'id': 'username '}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control input-border-bottom',
                                   'id': 'password'}))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label='',
        max_length=30,
        min_length=5,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control input-border-bottom"
            }
        )
    )
    first_name = forms.CharField(
        label='',
        max_length=9,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "7xxxxxxxx",
                "class": "form-control input-border-bottom"
            }
        )
    )


    email = forms.EmailField(
        label='',
        max_length=255,
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control input-border-bottom"
            }
        )
    )

    password1 = forms.CharField(
        label='',
        max_length=30,
        min_length=8,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control input-border-bottom"
            }
        )
    )

    password2 = forms.CharField(
        label='',
        max_length=30,
        min_length=8,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control input-border-bottom"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username','first_name','email', 'password1', 'password2')


class depositForm(forms.Form):
    amount = forms.FloatField(
        label='',
        max_value=1000000,
        min_value=1,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control input-solid",
                "placeholder": "Amount",
                "id": "inputFloatingLabel2"
            }
        )

    )
