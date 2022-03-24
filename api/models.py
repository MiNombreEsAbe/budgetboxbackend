from pyexpat import model
from statistics import mode
from unicodedata import category
from django.db import models
  
# Create your models here.

class User(models.Model):
    class Meta(object):
        db_table = "User"
    
    name = models.CharField("Name", blank=False, null=False, max_length=100)

    email = models.CharField("Email", blank=False, null=False, max_length=100)

    password = models.CharField("Password", blank=False, null=False, max_length=255)

    budget = models.IntegerField("Budget", blank=False, default=0, null=False)
    
    createdAt = models.DateTimeField("Created At", blank=True, auto_now_add=True)

    updatedAt = models.DateTimeField("Updated At", blank=True, auto_now=True)

    def getObject(self):
        data = {
            "name": self.name,
            "email": self.email,
            "budget": self.budget,
            "createdAt": self.createdAt
        }

        return data

    def __str__(self):
        return self.name

class Category(models.Model):
    class Meta(object):
        db_table = "Category"
        verbose_name_plural = "Categories"
    
    name = models.CharField("Name", blank=False, null=False, max_length=50, db_index=True)

    createdAt = models.DateTimeField("Created At", blank=True, auto_now_add=True)

    updatedAt = models.DateTimeField("Updated At", blank=True, auto_now=True)
    
    def __str__(self):
        return self.name

class MoneyEntry(models.Model):
    class Meta(object):
        db_table = "Money Entry"
        verbose_name_plural = "Money Entries"

    createdAt = models.DateTimeField('Created At', blank=True, auto_now_add=True)

    entryType = models.BooleanField("Expense Or Income", blank=True)

    amount = models.FloatField("Amount")

    name = models.CharField('Name', blank=False, null=False, max_length=30, db_index=True)

    userId = models.BigIntegerField("User Id", blank=False, null=False, default=2)

    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE, default=1)

    category = models.ForeignKey(Category, related_name="category", on_delete=models.CASCADE, default=1)

    date = models.DateField("Date", blank=False, null=True)

    createdAt = models.DateTimeField("Created At", blank=True, auto_now_add=True)

    updatedAt = models.DateTimeField("Updated At", blank=True, auto_now=True)

    def getObject(self):
        data = {
            "name": self.name,
            "entryType": self.entryType,
            "amount": self.amount,
            "createdAt": self.createdAt,
            "userId": self.user.id,
            "category": self.category,
            "date": self.date
        }

        return data

    def get_user_id(self):
        return self.user.id