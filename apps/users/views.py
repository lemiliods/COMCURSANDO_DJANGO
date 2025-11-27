from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import AdminUser
from .serializers import AdminUserSerializer, LoginSerializer
from .authentication import generate_jwt_token


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Endpoint de login que retorna token JWT.
    
    POST /api/auth/login
    Body: {"username": "...", "password": "..."}
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Credenciais inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Usuário inativo'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token = generate_jwt_token(user)
    
    return Response({
        'token': token,
        'user': AdminUserSerializer(user).data
    })


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar usuários administradores.
    Apenas leitura - GET /api/users/
    """
    queryset = AdminUser.objects.filter(is_active=True)
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['username', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']
