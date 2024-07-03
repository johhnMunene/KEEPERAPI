# models.py
from tortoise import fields, Tortoise
from tortoise.models import Model
from datetime import datetime

class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=50, null=False, unique=True)
    password = fields.CharField(max_length=128, null=False)
    is_verified = fields.BooleanField(default=False)
    join_date = fields.DatetimeField(default=datetime.utcnow)

class Keeper(Model):
    id = fields.IntField(pk=True, index=True)
    keeper = fields.CharField(max_length=15, null=False, unique=True)
    state = fields.CharField(max_length=100, null=False, default="unspecified")
    city = fields.CharField(max_length=100, null=False, default="unspecified")
    keeper_description = fields.TextField(null=True)
    logo = fields.CharField(max_length=200, null=False, default="default.jpg")
    owner = fields.ForeignKeyField("models.User", related_name="business")

class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, null=False)
    description = fields.TextField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=False)
    quantity = fields.IntField(null=False, default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    owner = fields.ForeignKeyField("models.User", related_name="products")
    image_url = fields.CharField(max_length=200, null=True, default="default.jpg")
    business = fields.ForeignKeyField("models.Keeper", related_name="products")

