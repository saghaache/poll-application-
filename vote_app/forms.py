from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Poll, Option

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'description', 'start_date', 'end_date', 'vote_type']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['name', 'description']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
