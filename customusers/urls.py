from django.urls import path
from .views import RegisterView, LoginView, MyUserView, UserList

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('my-user/', MyUserView.as_view(), name='my_user'),
    path('allUsers/', UserList.as_view(), name='allUsers'),
]