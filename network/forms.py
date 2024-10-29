# forms.py

from django import forms
from .models import User  # Assuming you have a UserProfile model for storing user info

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User  # Your model for the user profile
        fields = ['username','first_name', 'last_name', 'profile_pic', 'cover']  # Add any other fields you want to allow editing
