from django import forms
from .models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'profile_pic', 'cover'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_common_styles(self.fields)
        self.fields['profile_pic'].widget.attrs.update({
            'class': 'block w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'id': 'profile'
        })
        self.fields['cover'].widget.attrs.update({
            'class': 'block w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'id': 'cover'
        })

def add_common_styles(fields):
    for field_name, field in fields.items():
        field.widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': field.label
        })

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_common_styles(self.fields)

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'profile_pic', 'cover']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_common_styles(self.fields)
        self.fields['profile_pic'].widget.attrs.update({
            'class': 'block w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'id': 'profile'
        })
        self.fields['cover'].widget.attrs.update({
            'class': 'block w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'id': 'cover'
        })
