from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
 
    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def create(self, validated_data):

        password = validated_data.pop('password')
        hashed_password = make_password(password)

        user = User.objects.create(password=hashed_password, **validated_data)
        
        return user
