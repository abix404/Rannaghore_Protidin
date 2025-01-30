import uuid

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserInfo(models.Model):
    first_name=models.CharField(max_length=15,blank=False,null=False)
    last_name=models.CharField(max_length=15,blank=False,null=False)
    mobile_no=models.IntegerField(blank=False,null=False)
    email=models.EmailField()
    bio=models.CharField(max_length=200,null=True,blank=True)

class Products(models.Model):
    name=models.CharField(max_length=100,blank=False,null=False)
    p_id=models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    price=models.IntegerField(blank=True,null=True)
    categories=models.CharField(max_length=50,blank=True,null=True)
    short_description=models.CharField(max_length=100, blank=False,null=False)
    brief_description=models.CharField(max_length=500)
    brand=models.CharField(max_length=20)
    image=models.ImageField(upload_to='products_img', blank=True,null=True, default='no_image.png')
    sku=models.IntegerField(unique=True)
def __str__(self):
    return self.name

class Cart(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    product=models.ForeignKey(Products, on_delete=models.CASCADE,blank=True,null=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, blank=True, null=True)
    ctrate_date=models.DateTimeField(auto_now_add=True,auto_now=False)
    order_id=models.IntegerField(unique=True)







