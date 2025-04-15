from django.db import models

class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Role(models.Model):
    role = models.CharField(max_length=10)
    can_post_login = models.BooleanField(default=False)
    can_get_my_user = models.BooleanField(default=False)
    can_get_users = models.BooleanField(default=False)
    can_post_products = models.BooleanField(default=False)

class Product(models.Model):
    shopify_id = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    sales_count = models.IntegerField(default=0)