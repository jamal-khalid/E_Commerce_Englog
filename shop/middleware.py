from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import decode as jwt_decode, InvalidTokenError
from django.conf import settings
from django.contrib.auth import get_user_model

@database_sync_to_async
def get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return JWTAuthMiddlewareInstance(scope, self)

class JWTAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.scope = dict(scope)
        self.middleware = middleware

    async def __call__(self, receive, send):
        from rest_framework_simplejwt.tokens import UntypedToken
        # get token from query string
        query_string = self.scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")
        if token:
            token = token[0]
            try:
                UntypedToken(token)  # validate token
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get('user_id')
                self.scope['user'] = await get_user(user_id)
                close_old_connections()
            except InvalidTokenError:
                self.scope['user'] = AnonymousUser()
        else:
            self.scope['user'] = AnonymousUser()

        inner = self.middleware.inner(self.scope)
        return await inner(receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
