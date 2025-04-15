from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import PermissionDenied
from django.urls import resolve
from customusers.authorizer import get_user_from_token

class PermissionsMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Ne vérifie que les méthodes GET et POST
        if request.method not in ['GET', 'POST']:
            return None

        try:
            user = get_user_from_token(request)
        except Exception:
            return None
        
        request.user = user

        # On récupère le nom de l’endpoint (ex: 'register', 'login', etc)
        current_url_name = resolve(request.path_info).url_name

        # Logique de permission en fonction de l’URL
        if current_url_name == 'allUsers' and not user.role.can_get_users:
            raise PermissionDenied("Vous n'avez pas la permission de voir tous les utilisateurs.")
        
        if current_url_name == 'my_user' and not user.role.can_get_my_user:
            raise PermissionDenied("Vous n'avez pas la permission d'accéder à vos infos.")
        
        if current_url_name == 'login' and not user.role.can_post_login:
            raise PermissionDenied("Vous n'avez pas la permission de vous connecter.")
        
        if current_url_name == 'products_post' and not user.role.can_post_products:
            raise PermissionDenied("Ce rôle n'a pas le droit d'ajouter un produit.")
        
        return None

