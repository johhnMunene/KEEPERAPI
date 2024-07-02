from tortoise import fields, Tortoise
from tortoise.models import Model
from datetime import datetime

# User model represents a user in the system
class User(Model):
    id = fields.IntField(pk=True, index=True)  # Primary key
    username = fields.CharField(max_length=20, null=False, unique=True)  # Unique username
    email = fields.CharField(max_length=50, null=False, unique=True)  # Unique email
    password = fields.CharField(max_length=128, null=False)  # Password
    is_verified = fields.BooleanField(default=False)  # Verification status
    join_date = fields.DatetimeField(default=datetime.utcnow)  # Join date

# Keeper model represents a business or organization
class Keeper(Model):
    id = fields.IntField(pk=True, index=True)  # Primary key
    keeper = fields.CharField(max_length=15, null=False, unique=True)  # Unique keeper name
    state = fields.CharField(max_length=100, null=False, default="unspecified")  # State
    city = fields.CharField(max_length=100, null=False, default="unspecified")  # City
    keeper_description = fields.TextField(null=True)  # Description
    logo = fields.CharField(max_length=200, null=False, default="default.jpg")  # Logo URL
    owner = fields.ForeignKeyField("models.User", related_name="business")  # Foreign key to User

# Product model represents a product offered by a Keeper
class Product(Model):
    id = fields.IntField(pk=True, index=True)  # Primary key
    name = fields.CharField(max_length=100, null=False)  # Product name
    description = fields.TextField(null=True)  # Product description
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=False)  # Product price
    quantity = fields.IntField(null=False, default=0)  # Quantity available
    is_active = fields.BooleanField(default=True)  # Active status
    created_at = fields.DatetimeField(auto_now_add=True)  # Creation timestamp
    updated_at = fields.DatetimeField(auto_now=True)  # Update timestamp
    owner = fields.ForeignKeyField("models.User", related_name="products")  # Foreign key to User
    image_url = fields.CharField(max_length=200, null=True, default="default.jpg")  # Image URL
    business = fields.ForeignKeyField("models.Keeper", related_name="products")  # Foreign key to Keeper

