from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(blank=True)
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),  # legacy
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True)
    level = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)
    badges = models.ManyToManyField('Badge', blank=True, related_name='users')
    verification_code = models.CharField(max_length=4, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    courses_enrolled = models.ManyToManyField('courses.Course', blank=True)
    courses_completed = models.ManyToManyField('courses.Course', blank=True, related_name='completed_by')
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class Badge(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.name