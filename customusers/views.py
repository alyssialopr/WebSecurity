from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from .serializers import RegisterSerializer
from django.contrib.auth.hashers import check_password
from customusers.models import User, Role
from customusers.authorizer import get_user_from_token

import jwt
from datetime import datetime, timedelta
from django.conf import settings

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            role_user = Role.objects.get(role="USER")
            user = serializer.save()
            user.role = role_user
            user.save()
            return Response({"message": "Utilisateur créé avec succès ✅"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        name = request.data.get("name")
        password = request.data.get("password")

        if name:
            try:
                user = User.objects.get(name=name)
            except User.DoesNotExist:
                user = None

        if user and check_password(password, user.password):
            if not user.role or not user.role.can_post_login:
                return Response({'detail': "Vous n'avez pas le droit de vous connecter."}, status=status.HTTP_403_FORBIDDEN)

            # Si l'utilisateur est trouvé, créer un JWT
            payload = {
                'id': user.id,
                'name': user.name,
                'exp': datetime.now() + timedelta(hours=1)  # Le token est valable 1 heure
            }

            # Créer un token JWT
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({'token': token}, status=status.HTTP_200_OK)
        
        # Si l'utilisateur n'est pas trouvé ou les identifiants sont incorrects
        return Response({'detail': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)
    
class MyUserView(APIView):
    def get(self, request):
        try:
            user = get_user_from_token(request)
            return Response({
                'name': user.name,
                'email': user.email
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserList(APIView):
    def get(self, request):

        try:
            get_user_from_token(request)
            users = User.objects.all()
            return Response({
                'users': [{'name': u.name, 'email': u.email} for u in users]
            }
            , status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
