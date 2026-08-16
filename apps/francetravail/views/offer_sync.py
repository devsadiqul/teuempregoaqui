from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from apps.francetravail import services
from apps.francetravail.serializers import OfferSyncRequestSerializer


@swagger_auto_schema(
    method="post",
    operation_id="offer_sync",
    operation_summary="Sync live France Travail offers into the mirror",
    request_body=OfferSyncRequestSerializer,
    responses={200: "Sync stats (created, updated, seen, purged)", 502: "Upstream error"},
    tags=["France Travail"],
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def offer_sync(request):
    req = OfferSyncRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    d = req.validated_data
    try:
        stats = services.sync_offers(
            code_rome=d.get("rome"), mots_cles=d.get("mots_cles"),
            departement=d.get("departement"), max_offers=d.get("max_offers", 150))
    except Exception as exc:
        return Response({"detail": f"Upstream sync failed: {exc}"},
                        status=status.HTTP_502_BAD_GATEWAY)
    stats["purged"] = services.purge_stale(stats.pop("seen_ids"))
    return Response(stats)
