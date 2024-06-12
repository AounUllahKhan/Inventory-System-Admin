from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='category_images/%y', null=True, blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='item_images/%y', null=True, blank=True)

    def __str__(self):
        return self.name
