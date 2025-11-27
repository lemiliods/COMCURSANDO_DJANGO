import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import AdminUser


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Autenticação customizada usando JWT.
    Espera o token no header: Authorization: Bearer <token>
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token inválido')
        
        try:
            user = AdminUser.objects.get(id=payload['user_id'])
        except AdminUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('Usuário não encontrado')
        
        if not user.is_active:
            raise exceptions.AuthenticationFailed('Usuário inativo')
        
        return (user, token)


def generate_jwt_token(user):
    """
    Gera um token JWT para o usuário.
    
    Args:
        user: Instância do modelo AdminUser
    
    Returns:
        str: Token JWT codificado
    """
    expiration = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm='HS256'
    )
    
    return token
