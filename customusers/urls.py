from django.urls import path
from .views import RegisterView, LoginView, MyUserView, UserList, ProductCreateView, MyProductsView, AllProductsView, ShopifySalesWebhookView 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('my-user/', MyUserView.as_view(), name='my_user'),
    path('allUsers/', UserList.as_view(), name='allUsers'),

    path('products/', ProductCreateView.as_view(), name='products_post'),
    path('my-products/', MyProductsView.as_view(), name='my_products'),
    path('products/all/', AllProductsView.as_view(), name='all_products'),

    path('webhooks/shopify-sales/', ShopifySalesWebhookView.as_view(), name='shopify_sales_webhook'),
]