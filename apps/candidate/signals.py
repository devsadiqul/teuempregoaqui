from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CandidateProfile
from .tasks import sync_profile_status_to_users_service


@receiver(post_save, sender=CandidateProfile)
def trigger_profile_sync(sender, instance, **kwargs):
    sync_profile_status_to_users_service.delay(instance.id)