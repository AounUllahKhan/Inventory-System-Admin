from django import forms
from .models import Category, Item
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','image']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'quantity','image']

class WarehouseSignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()   # Use the custom user model
        fields = ['username', 'email', 'password1', 'password2']

        
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()  # Use get_user_model() instead of User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)


class ItemUploadForm(forms.Form):
    csv_file = forms.FileField(required=False)
    