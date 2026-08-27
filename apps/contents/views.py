from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema, no_body
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from drf_yasg import openapi
from django.db.models import F
from .utils import get_user_info


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: NewsCategorySerializer(many=True)},
    tags=['News Category']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    if request.user.is_authenticated and request.user.is_staff:
        categories = NewsCategory.objects.all()
    else:
        categories = NewsCategory.objects.filter(is_active=True)
    serializer = NewsCategorySerializer(categories, many=True, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=NewsCategorySerializer,
    responses={201: NewsCategorySerializer()},
    tags=['News Category']
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    serializer = NewsCategorySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Category created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='patch',
    request_body=NewsCategorySerializer,
    responses={200: NewsCategorySerializer()},
    tags=['News Category']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_category(request, pk):
    category = get_object_or_404(NewsCategory, pk=pk)
    serializer = NewsCategorySerializer(category, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Category updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    responses={200: 'Category deleted successfully'},
    tags=['News Category']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_category(request, pk):
    category = get_object_or_404(NewsCategory, pk=pk)
    category.delete()
    return Response(
        {"message": "Category deleted successfully"},
        status=status.HTTP_200_OK
    )


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: NewsSerializer(many=True)},
    tags=['News']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_news(request):
    if request.user.is_authenticated and request.user.is_staff:
        news = News.objects.all()
    else:
        news = News.objects.filter(is_published=True)
    serializer = NewsSerializer(news, many=True, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=NewsSerializer,
    responses={201: NewsSerializer()},
    tags=['News']
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_news(request):
    serializer = NewsSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user_info = get_user_info(user.id)
        author_name = user_info.get('name', 'Unknown User') if user_info else 'Unknown User'
        author_avatar = user_info.get('image', None) if user_info else None
        serializer.save(
            author_id=str(user.id),
            author_name=author_name,
            author_avatar_url=author_avatar
        )
        return Response(
            {"message": "News created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: NewsSerializer()},
    tags=['News']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_detail(request, slug):
    try:
        if request.user.is_authenticated and request.user.is_staff:
            news = News.objects.get(slug=slug)
        else:
            news = News.objects.get(slug=slug, is_published=True)
        News.objects.filter(pk=news.pk).update(views_count=F('views_count') + 1)
        news.refresh_from_db()
        serializer = NewsSerializer(news, context={'request': request})
        return Response(serializer.data)
    except News.DoesNotExist:
        return Response({"detail": "News not found."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='patch',
    request_body=NewsSerializer,
    responses={200: NewsSerializer()},
    tags=['News']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_news(request, slug):
    news = get_object_or_404(News, slug=slug)
    serializer = NewsSerializer(news, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "News updated successfully.", "data": serializer.data})
    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    responses={200: 'Deleted'},
    tags=['News']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_news(request, slug):
    try:
        news = News.objects.get(slug=slug)
        news.delete()
        return Response({"message": "News deleted successfully."}, status=status.HTTP_200_OK)
    except News.DoesNotExist:
        return Response({"detail": "News not found."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: ArticleCategorySerializer(many=True)},
    tags=['Article Category']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_article_category_list(request):
    if request.user.is_authenticated and request.user.is_staff:
        categories = ArticleCategory.objects.all()
    else:
        categories = ArticleCategory.objects.filter(is_active=True)
    serializer = ArticleCategorySerializer(categories, many=True, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=ArticleCategorySerializer,
    responses={201: ArticleCategorySerializer()},
    tags=['Article Category']
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_article_category(request):
    serializer = ArticleCategorySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Article category created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: ArticleCategorySerializer()},
    tags=['Article Category']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_article_category(request, slug):
    if request.user.is_authenticated and request.user.is_staff:
        category = get_object_or_404(ArticleCategory, slug=slug)
    else:
        category = get_object_or_404(ArticleCategory, slug=slug, is_active=True)
    serializer = ArticleCategorySerializer(category, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='patch',
    request_body=ArticleCategorySerializer,
    responses={200: ArticleCategorySerializer()},
    tags=['Article Category']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_article_category(request, slug):
    category = get_object_or_404(ArticleCategory, slug=slug)
    serializer = ArticleCategorySerializer(category, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Article category updated successfully.", "data": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'},
    tags=['Article Category']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_article_category(request, slug):
    category = get_object_or_404(ArticleCategory, slug=slug)
    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: ArticleSerializer(many=True)},
    tags=['Article']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_article_list(request):
    if request.user.is_authenticated and request.user.is_staff:
        articles = Article.objects.all()
    else:
        articles = Article.objects.filter(is_published=True)
    serializer = ArticleSerializer(articles, many=True, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['title', 'content'],
        properties={
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'content': openapi.Schema(type=openapi.TYPE_STRING),
            'official_source_label': openapi.Schema(type=openapi.TYPE_STRING),
            'official_source_url': openapi.Schema(type=openapi.TYPE_STRING),
            'is_published': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={201: ArticleSerializer()},
    tags=['Article']
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_article(request):
    serializer = ArticleSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Article created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: ArticleSerializer()},
    tags=['Article']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_article(request, slug):
    if request.user.is_authenticated and request.user.is_staff:
        article = get_object_or_404(Article, slug=slug)
    else:
        article = get_object_or_404(Article, slug=slug, is_published=True)
    serializer = ArticleSerializer(article, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='patch',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'content': openapi.Schema(type=openapi.TYPE_STRING),
            'official_source_label': openapi.Schema(type=openapi.TYPE_STRING),
            'official_source_url': openapi.Schema(type=openapi.TYPE_STRING),
            'is_published': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={200: ArticleSerializer()},
    tags=['Article']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    serializer = ArticleSerializer(article, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Article updated successfully.", "data": serializer.data})
    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'},
    tags=['Article']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    article.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of official sources",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "url": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                    },
                ),
            ),
        )
    },
    tags=['Official Source']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def official_source_names(request):
    sources = OfficialSource.objects.filter(is_active=True).values(
        "name",
        "url",
    )
    return Response(list(sources))


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (description language; default en)", type=openapi.TYPE_STRING),
        openapi.Parameter('country', openapi.IN_QUERY, description="Filter by ISO country code, e.g. PT, ES, FR", type=openapi.TYPE_STRING),
    ],
    responses={200: OfficialSourceSerializer(many=True)},
    tags=['Official Source']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_official_source_list(request):
    if request.user.is_authenticated and request.user.is_staff:
        sources = OfficialSource.objects.all()
    else:
        sources = OfficialSource.objects.filter(is_active=True)
    country = request.query_params.get('country')
    if country:
        sources = sources.filter(country__country_code__iexact=country)
    serializer = OfficialSourceSerializer(sources, many=True, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=OfficialSourceSerializer,
    responses={201: OfficialSourceSerializer()},
    tags=['Official Source']
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_official_source(request):
    serializer = OfficialSourceSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Official source created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
    ],
    responses={200: OfficialSourceSerializer()},
    tags=['Official Source']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_official_source(request, pk):
    if request.user.is_authenticated and request.user.is_staff:
        source = get_object_or_404(OfficialSource, pk=pk)
    else:
        source = get_object_or_404(OfficialSource, pk=pk, is_active=True)
    serializer = OfficialSourceSerializer(source, context={'request': request})
    return Response(serializer.data)

@swagger_auto_schema(
    method='patch',
    request_body=OfficialSourceSerializer(partial=True),
    responses={200: OfficialSourceSerializer()},
    tags=['Official Source']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_official_source(request, pk):
    source = get_object_or_404(OfficialSource, pk=pk)
    serializer = OfficialSourceSerializer(source, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Official source updated successfully.", "data": serializer.data})
    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'},
    tags=['Official Source']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_official_source(request, pk):
    source = get_object_or_404(OfficialSource, pk=pk)
    source.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="en | es | pt (default en)", type=openapi.TYPE_STRING),
        openapi.Parameter('is_active', openapi.IN_QUERY, description="Filter by active status (true/false)", type=openapi.TYPE_BOOLEAN),
    ],
    responses={200: FAQSerializer(many=True)},
    tags=['FAQ']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_faq_list(request):
    lang = (request.query_params.get('lang') or 'en').lower()[:2]
    if lang not in ('en', 'es', 'pt'):
        lang = 'en'

    if request.user.is_authenticated and request.user.is_staff:
        faqs = FAQ.objects.all()
    else:
        faqs = FAQ.objects.filter(is_active=True)

    lang_faqs = faqs.filter(language=lang)
    if not lang_faqs.exists() and lang != 'en':
        lang_faqs = faqs.filter(language='en')
    faqs = lang_faqs

    is_active = request.query_params.get('is_active')
    if is_active is not None:
        faqs = faqs.filter(is_active=is_active.lower() == 'true')

    serializer = FAQSerializer(faqs, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    responses={200: FAQSerializer()},
    tags=['FAQ']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_faq(request, pk):
    if request.user.is_authenticated and request.user.is_staff:
        faq = get_object_or_404(FAQ, pk=pk)
    else:
        faq = get_object_or_404(FAQ, pk=pk, is_active=True)
    serializer = FAQSerializer(faq)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=FAQSerializer,
    responses={201: FAQSerializer()},
    tags=['FAQ']
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_faq(request):
    serializer = FAQSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "FAQ created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='patch',
    request_body=FAQSerializer,
    responses={200: FAQSerializer()},
    tags=['FAQ']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_faq(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    serializer = FAQSerializer(faq, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "FAQ updated successfully.", "data": serializer.data}
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'},
    tags=['FAQ']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_faq(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category", type=openapi.TYPE_STRING),
        openapi.Parameter('is_resolved', openapi.IN_QUERY, description="Filter by resolved status (true/false)", type=openapi.TYPE_BOOLEAN),
    ],
    responses={200: FeedbackSerializer(many=True)},
    tags=['Feedback']
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_feedback_list(request):
    feedbacks = Feedback.objects.all()
    category = request.query_params.get('category')
    is_resolved = request.query_params.get('is_resolved')
    if category:
        feedbacks = feedbacks.filter(category=category)
    if is_resolved is not None:
        feedbacks = feedbacks.filter(is_resolved=is_resolved.lower() == 'true')
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    responses={200: FeedbackSerializer()},
    tags=['Feedback']
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    serializer = FeedbackSerializer(feedback)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=FeedbackSerializer,
    responses={201: FeedbackSerializer()},
    tags=['Feedback']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_feedback(request):
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user_id=str(request.user.id))
        return Response(
            {"message": "Feedback submitted successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='patch',
    request_body=no_body,
    responses={200: FeedbackSerializer()},
    tags=['Feedback']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def resolve_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.is_resolved = not feedback.is_resolved
    feedback.save()
    serializer = FeedbackSerializer(feedback)
    return Response(serializer.data)

@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'},
    tags=['Feedback']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)