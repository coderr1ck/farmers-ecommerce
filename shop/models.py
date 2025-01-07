from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Custom User model with roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Farmer', 'Farmer'),
        ('Consumer', 'Consumer'),
    )
    address = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Consumer')

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):
    ORGANIC = 'Organic'
    INORGANIC = 'Inorganic'
    TYPE_CHOICES = [
        (ORGANIC, 'Organic'),
        (INORGANIC, 'Inorganic'),
    ]

    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="items")    
    image = models.ImageField(upload_to='static/images/item_images/')
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    size = models.CharField(max_length=100)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    ordered_date = models.DateTimeField(auto_now_add=True)
    billing_address = models.TextField()
    shipping_address = models.TextField()
    status = models.CharField(max_length=50, default='Pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    @property
    def get_total_order_price(self):
        total = sum(order_item.get_total_item_price for order_item in self.orderitem_set.all())
        return total


class Transaction(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Transaction {self.transaction_id} for {self.user.username}"


class Review(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    feedback = models.TextField()

    def __str__(self):
        return f"Review for {self.item.name} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    # Update the total calculation for each order item
    @property
    def get_total_item_price(self):
        return self.quantity * self.item.price