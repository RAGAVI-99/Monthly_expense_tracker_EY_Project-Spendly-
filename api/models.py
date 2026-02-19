from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    def __str__(self): return self.username

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    def __str__(self): return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    note = models.CharField(max_length=255, blank=True)
    date = models.DateField()

class Income(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=128)
    date = models.DateField()
