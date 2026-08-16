from rest_framework import serializers
from .models import Legal


class LegalSerializer(serializers.ModelSerializer):
    # language is writable (for create/upsert) but kept out of the read payload
    # so the response shape stays identical to the pre-multilingual API.
    language = serializers.CharField(write_only=True, required=False, default='en')

    class Meta:
        model = Legal
        fields = ['id', 'document_type', 'language', 'title', 'content',
                  'version', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['version', 'created_at', 'updated_at']
