from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import  SignUpView,Dashboard,Index

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:category_id>/items/', views.item_list, name='item_list'),
    path('categories/<int:category_id>/items/new/', views.item_create, name='item_create'),
    path('categories/<int:category_id>/items/<int:pk>/edit/', views.item_update, name='item_update'),
    path('categories/<int:category_id>/items/<int:pk>/delete/', views.item_delete, name='item_delete'),
]
