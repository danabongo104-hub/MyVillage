from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    PARENT = 'parent'
    THERAPIST = 'therapist'
    ROLE_CHOICES = [
        (PARENT, 'Parent'),
        (THERAPIST, 'Therapist'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_parent(self):
        return self.role == self.PARENT

    @property
    def is_therapist(self):
        return self.role == self.THERAPIST


class ParentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    number_of_children = models.PositiveIntegerField(default=0)
    children_age_range = models.CharField(max_length=50, blank=True, null=True)
    concerns = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Parent Profile: {self.user.username}"


class TherapistProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='therapist_profile'
    )
    license_number = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    accepting_clients = models.BooleanField(default=True)

    def __str__(self):
        return f"Therapist Profile: {self.user.username}"