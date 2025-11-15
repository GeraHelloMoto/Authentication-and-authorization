from django.http import JsonResponse
import jwt
from django.conf import settings
from .models import User


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id, is_active=True)
                request.user = user
            except:
                request.user = None
        else:
            request.user = None

        return self.get_response(request)