from celery import shared_task
from django.conf import settings
import requests
from .models import CandidateProfile


def is_assessment_complete(profile: CandidateProfile) -> bool:
    return bool(
        profile.education.exists()
        and profile.experiences.exists()
        and profile.languages.exists()
    )


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def sync_profile_status_to_users_service(self, profile_id):
    profile = CandidateProfile.objects.get(id=profile_id)
    payload = {
        'candidate_profile_id': profile.id,
        'has_completed_assessment': is_assessment_complete(profile),
    }
    try:
        requests.post(
            f'{settings.OIT_BACKBONE_URL}/users/{profile.user_id}/candidate-profile-sync/',
            json=payload,
            headers={'X-Internal-Secret': settings.SECRET_KEY},
            timeout=3,
        )
    except requests.RequestException as exc:
        raise self.retry(exc=exc)


@shared_task
def resync_all_candidate_profiles():
    profile_ids = CandidateProfile.objects.values_list('id', flat=True)
    for profile_id in profile_ids:
        sync_profile_status_to_users_service.delay(profile_id)