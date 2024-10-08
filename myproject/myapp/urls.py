from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import  Dashboard, Index, warehouse_signup, user_signup, user_login, warehouse_login

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:category_id>/items/', views.item_list, name='item_list'),
    path('categories/<int:category_id>/items/new/', views.item_create, name='item_create'),
    path('categories/<int:category_id>/items/<int:pk>/edit/', views.item_update, name='item_update'),
    path('categories/<int:category_id>/items/<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('user_signup/', user_signup, name='user_signup'),
    path('warehouse_signup/', warehouse_signup, name='warehouse_signup'),
    path('user_login/', user_login, name='user_login'),
    path('warehouse_login/', warehouse_login, name='warehouse_login'),
    path('logout/warehouse/', views.warehouse_logout, name='warehouse_logout'),
    path('logout/user/', views.user_logout, name='user_logout'),
]
