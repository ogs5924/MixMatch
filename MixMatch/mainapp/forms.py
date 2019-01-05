from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Please enter your first name.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Please enter your last name.')
    gender = forms.ChoiceField(choices=User.GENDERS, required=True)
    dob = forms.DateField(required=True, widget=forms.TextInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'gender', 'dob')
