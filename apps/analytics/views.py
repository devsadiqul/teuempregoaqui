from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from apps.contents.models import News, Article, Feedback
from apps.francetravail.models import JobOffer
from .serializers import DashboardSummarySerializer, FeedbackSummarySerializer
from django.utils import timezone
from dateutil.relativedelta import relativedelta


@swagger_auto_schema(
    method='get',
    operation_summary='Dashboard summary',
    responses={200: DashboardSummarySerializer},
    tags=['Analytics'],
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_summary(request):
    data = {
        'total_news':          News.objects.filter(is_published=True).count(),
        'total_articles':      Article.objects.filter(is_published=True).count(),
        'total_jobs':          JobOffer.objects.filter(is_active=True).count(),
        'avg_feedback_rating': round(Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
    }
    return Response(DashboardSummarySerializer(data).data)


@swagger_auto_schema(
    method='get',
    operation_summary='Feedback summary',
    responses={200: FeedbackSummarySerializer},
    tags=['Analytics'],
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def feedback_summary(request):
    qs = Feedback.objects.all()
    data = {
        'total_feedbacks':     qs.count(),
        'pending_feedbacks':   qs.filter(is_resolved=False).count(),
        'resolved_feedbacks':  qs.filter(is_resolved=True).count(),
        'avg_feedback_rating': round(qs.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
    }
    return Response(FeedbackSummarySerializer(data).data)


@swagger_auto_schema(
    method='get',
    operation_summary='Monthly Job Postings Chart',
    operation_description='Returns active job counts grouped by month. Filter with `year` or `months`.',
    manual_parameters=[
        openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('months', openapi.IN_QUERY, description='Last N months', type=openapi.TYPE_INTEGER, required=False),
    ],
    tags=['Analytics'],
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def job_postings(request):
    qs = JobOffer.objects.filter(is_active=True)
    year = request.query_params.get('year')
    if year:
        qs = qs.filter(first_seen__year=int(year))

    months_limit = request.query_params.get('months')
    if months_limit:
        cutoff = timezone.now() - relativedelta(months=int(months_limit))
        qs = qs.filter(first_seen__gte=cutoff)

    qs = (
        qs.annotate(month=TruncMonth('first_seen'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    data = [
        {
            'month': entry['month'].strftime('%b'),
            'year': entry['month'].year,
            'count': entry['count'],
        }
        for entry in qs
        if entry['month'] is not None
    ]
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary='Recently Added Jobs',
    operation_description='Returns the most recently added jobs. Use `limit` to control how many.',
    manual_parameters=[
        openapi.Parameter('limit', openapi.IN_QUERY, description='Number of jobs to return (default 5)', type=openapi.TYPE_INTEGER, required=False),
    ],
    tags=['Analytics'],
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def recently_added_jobs(request):
    limit = int(request.query_params.get('limit', 5))
    jobs = JobOffer.objects.order_by('-first_seen')[:limit]
    data = [
        {
            'title': job.title,
            'company': job.company_name,
            'location': job.location,
            'is_active': job.is_active,
        }
        for job in jobs
    ]
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_summary='Latest Published News',
    operation_description='Returns the most recently published news. Use `limit` to control how many.',
    manual_parameters=[
        openapi.Parameter('limit', openapi.IN_QUERY, description='Number of news to return (default 5)', type=openapi.TYPE_INTEGER, required=False),
    ],
    tags=['Analytics'],
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def latest_published_news(request):
    limit = int(request.query_params.get('limit', 5))
    news  = News.objects.filter(is_published=True).order_by('-created_at')[:limit]

    data = [
        {
            'title':        item.title,
            'author_name':  item.author_name,
            'published_at': item.created_at.strftime('%Y-%m-%d'),
            'is_published': item.is_published,
        }
        for item in news
    ]

    return Response(data)