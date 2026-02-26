from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ParentProfile, TherapistProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.PARENT:
            ParentProfile.objects.create(user=instance)
        elif instance.role == User.THERAPIST:
            TherapistProfile.objects.create(user=instance)