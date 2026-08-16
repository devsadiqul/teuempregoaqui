from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

class RemoteJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        User = get_user_model()
        user = User(id=user_id)
        user.is_active    = validated_token.get('is_active', True)
        user.is_staff     = validated_token.get('is_staff', False)
        user.is_superuser = validated_token.get('is_superuser', False)
        return user