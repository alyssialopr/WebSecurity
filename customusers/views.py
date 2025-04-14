from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django.contrib.auth.hashers import check_password
from customusers.models import User

import jwt
from datetime import datetime, timedelta
from django.conf import settings

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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
            # Si l'utilisateur est trouvé, créer un JWT
            payload = {
                'id': user.id,
                'name': user.name,
                'exp': datetime.utcnow() + timedelta(hours=1)  # Le token est valable 1 heure
            }

            # Créer un token JWT
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({'token': token}, status=status.HTTP_200_OK)
        
        # Si l'utilisateur n'est pas trouvé ou les identifiants sont incorrects
        return Response({'detail': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)