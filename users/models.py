from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)  # Additional field for user's bio
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)

      # Override related_name for groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Custom related name to avoid conflict
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Custom related name to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

