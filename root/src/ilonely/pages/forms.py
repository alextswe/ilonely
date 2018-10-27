from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from pages.models import Document
from django.contrib.auth.models import User
from django import forms
from pages.models import Profile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomUserCreationForm(UserCreationForm):
    # User fields
    username = forms.CharField(label='Enter Username')
    firstname = forms.CharField(label='Enter First Name')
    lastname = forms.CharField(label='Enter Last Name')
    email = forms.EmailField(label='Enter email')
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'firstname', 'lastname', 'email', 'password1', 'password2',)

    # Checks if username is taken
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError(_("Username is taken."), code='usernameError' )
        return username

    # Checks if an email is already associated with an account
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError(_("Email is already linked to an account."), code='emailError')
        return email

    # Checks if passwords match
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Password do not match."), code='passwordError')

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
        )
        user.first_name = self.cleaned_data['firstname']
        user.last_name = self.cleaned_data['lastname']
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('age',)

    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age < 18:
            raise ValidationError(_(""), code='ageError')

        return age

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document', )
