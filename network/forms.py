from django import forms
from .models import User

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'profile_pic', 'cover'] 
