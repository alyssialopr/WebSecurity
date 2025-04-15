import jwt
from django.conf import settings
from customusers.models import User
from rest_framework.exceptions import AuthenticationFailed

def get_user_from_token(request):
    token = request.headers.get('Authorization')

    if not token:
        raise AuthenticationFailed('Token manquant')
    
    try:
        # Décoder le token JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['id'])
        
        return user
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token expiré')
    except jwt.DecodeError:
        raise AuthenticationFailed('Token invalide')
    except User.DoesNotExist:
        raise AuthenticationFailed('Utilisateur non trouvé')