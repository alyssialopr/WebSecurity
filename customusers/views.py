import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from .serializers import RegisterSerializer
from django.contrib.auth.hashers import check_password
from customusers.models import User, Role, Product
from customusers.authorizer import get_user_from_token
from decouple import config
import hmac
import base64
import hashlib
import json


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

class ProductCreateView(APIView):
    def post(self, request):
        user = get_user_from_token(request)

        name = request.data.get("name")
        price = request.data.get("price")

        if not name or not price:
            return Response({'detail': "Nom et prix sont requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Shopify config

        SHOPIFY_API_KEY = config('SHOPIFY_API_KEY')
        SHOPIFY_STORE = config('SHOPIFY_STORE')

        url = f'https://{SHOPIFY_STORE}/admin/api/2023-01/products.json'
        headers = {
            'X-Shopify-Access-Token': SHOPIFY_API_KEY,
            'Content-Type': 'application/json'
        }

        data = {
            "product" : {
                "title": name,
                "variants" : [{
                    "price" : price
                }]
            }
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            product_data = response.json()['product']
            shopify_id = str(product_data['id'])

            # Enregistrement dans supabase
            Product.objects.create(
                shopify_id=shopify_id,
                created_by=user
            )
            
            return Response({"message": "Produit créé avec succès"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Erreur lors de la création du produit sur Shopify"}, status=status.HTTP_400_BAD_REQUEST)

class MyProductsView(APIView):
    def get(self, request):
        user = get_user_from_token(request)
        products = Product.objects.filter(created_by=user)

        if not user:
            return Response({'detail': "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'products': [
                {
                    'shopify_id': p.shopify_id,
                    'sales_count': p.sales_count
                } for p in products
            ]
        }, status=status.HTTP_200_OK)

class AllProductsView(APIView):

    def get(self, request):
        user = get_user_from_token(request)
        products = Product.objects.all()

        if not user:
            return Response({'detail': "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'products': [
                {
                    'shopify_id': p.shopify_id,
                    'sales_count': p.sales_count,
                    'created_by': p.created_by.name
                } for p in products
            ]
        }, status=status.HTTP_200_OK)
    
class ShopifySalesWebhookView(APIView):
    def post(self, request):
        SHOPIFY_WEBHOOK_SECRET = config('SHOPIFY_WEBHOOK_SECRET')

        # Vérification de la signature HMAC
        hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
        body = request.body

        calculated_hmac = base64.b64encode(
            hmac.new(
               SHOPIFY_WEBHOOK_SECRET.encode('utf-8'),
               body,
               hashlib.sha256
            ).digest()
        ).decode('utf-8')

        if not hmac.compare_digest(hmac_header, calculated_hmac):
            return Response({'detail': 'Signature HMAC invalide'}, status=status.HTTP_403_FORBIDDEN)
        
        payload = json.loads(body)
        line_items = payload.get('line_items', [])

        for item in line_items:
            shopify_product_id = str(item.get('product_id'))
            quantity = int(item.get('quantity', 0))

            try:
                product = Product.objects.get(shopify_id=shopify_product_id)
                product.sales_count += quantity
                product.save()
            except:
                continue
        
        return Response({'detail': 'Webhook traité avec succès'}, status=status.HTTP_200_OK)