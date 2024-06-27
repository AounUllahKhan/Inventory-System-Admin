from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from .models import Category, Item, User, Warehouse
from .forms import CategoryForm, ItemForm, UserRegisterForm, WarehouseSignUpForm, LoginForm, ItemUploadForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.sessions.models import Session
import csv
import io
from django.contrib import messages

class Index(TemplateView):
    template_name = 'index.html'

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_warehouse:
            categories = Category.objects.filter(warehouse=request.user.warehouse)
            return render(request, 'dashboard.html', {'categories': categories})
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
            
def warehouse_signup(request):
    if request.method == 'POST':
        form = WarehouseSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_warehouse = True
            user.save()
            warehouse = Warehouse.objects.create(name=f"{user.username}'s Warehouse", location='Default location', manager=user)
            user.warehouse = warehouse
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = WarehouseSignUpForm()
    return render(request, 'signup.html', {'form': form})

def warehouse_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None and user.is_active and user.is_warehouse:
                login(request, user)
                return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_signup(request):
    if not request.user.is_authenticated or not request.user.is_warehouse:
        return redirect('warehouse_login')  # Ensure warehouse user is logged in first

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_user = True
            user.warehouse = request.user.warehouse
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'user_signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                if user.is_superuser:
                    login(request, user)
                    return redirect('/admin/')
                elif user.is_user:  # Adjust this condition based on your model
                    # Check if the user has access to the warehouse
                    if hasattr(user, 'warehouse') and user.warehouse == request.user.warehouse:
                        login(request, user)
                        return redirect('category_list')
                    else:
                        messages.error(request, "You do not have permission to access this warehouse.")
                else:
                    messages.error(request, "Invalid login credentials.")
            else:
                messages.error(request, "Invalid login credentials.")
        
    else:
        form = LoginForm()
    return render(request, 'user_login.html', {'form': form})

def logout_associated_users(warehouse):
    associated_users = User.objects.filter(warehouse=warehouse, is_user=True)
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())

    for session in active_sessions:
        session_data = session.get_decoded()
        session_user_id = session_data.get('_auth_user_id')
        session_warehouse_id = session_data.get('warehouse_id')

        if session_user_id and session_warehouse_id:
            user = User.objects.filter(id=session_user_id).first()
            if user and user in associated_users and session_warehouse_id == warehouse.id:
                session.delete()

@login_required
@require_POST
def warehouse_logout(request):
    warehouse = request.user.warehouse
    logout_associated_users(warehouse)
    logout(request)  # Logout the current warehouse
    return render(request, 'logout.html')

@login_required
@require_POST
def user_logout(request):
    logout(request)  # Logout the current user
    return render(request, 'user_logout.html')

@login_required
def category_list(request):
    categories = Category.objects.filter(warehouse=request.user.warehouse)
    return render(request, 'category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.warehouse = request.user.warehouse
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.warehouse == request.user.warehouse:
        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES, instance=category)
            if form.is_valid():
                form.save()
                return redirect('category_list')
        else:
            form = CategoryForm(instance=category)
        return render(request, 'category_form.html', {'form': form})
    else:
        return HttpResponseForbidden("You do not have permission to edit this category.")

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.warehouse == request.user.warehouse:
        if request.method == 'POST':
            category.delete()
            return redirect('category_list')
        else:
            return render(request, 'category_confirm_delete.html', {'category': category})
    else:
        return HttpResponseForbidden("You do not have permission to delete this category.")

@login_required
def item_list(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    items = Item.objects.filter(category=category)
    alert = any(item.quantity < 25 for item in items)
    return render(request, 'item_list.html', {'category': category, 'items': items, 'alert': alert})


import os
from django.conf import settings
import chardet
@login_required
def item_create(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    
    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'This is not a CSV file.')
                return redirect('item_create', category_id=category.id)

            try:
                # Detect the file encoding using chardet
                raw_data = csv_file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']

                # Decode the file data using the detected encoding
                file_data = raw_data.decode(encoding)
                csv_reader = csv.DictReader(io.StringIO(file_data))

                # Check for the required headers
                if not set(csv_reader.fieldnames) >= {'name', 'description', 'quantity', 'image'}:
                    messages.error(request, 'CSV file must have name, description, quantity, and image fields.')
                    return redirect('item_create', category_id=category.id)

                for row in csv_reader:
                    name = row['name'].strip()
                    description = row['description'].strip()
                    quantity = int(row['quantity'].strip())
                    image_file = row['image'].strip()

                    # Construct the relative image path
                    image_path = os.path.join(settings.MEDIA_ROOT, image_file)

                    # Ensure the image path is within MEDIA_ROOT
                    if not os.path.commonprefix([settings.MEDIA_ROOT, image_path]) == settings.MEDIA_ROOT:
                        messages.error(request, f'Invalid image path: {image_file}')
                        return redirect('item_create', category_id=category.id)

                    # Create the Item object
                    item = Item.objects.create(
                        name=name,
                        description=description,
                        quantity=quantity,
                        image=image_file,  # Save the relative path
                        category=category
                    )

                messages.success(request, 'CSV file has been uploaded successfully.')
                return redirect('item_list', category_id=category.id)

            except Exception as e:
                print(f'Error uploading CSV file: {e}')
                messages.error(request, f'Error uploading CSV file: {e}')
                return redirect('item_create', category_id=category.id)

        else:
            form = ItemForm(request.POST, request.FILES)
            if form.is_valid():
                item = form.save(commit=False)
                item.category = category
                item.save()
                return redirect('item_list', category_id=category.id)

    else:
        form = ItemForm()

    return render(request, 'item_form.html', {'form': form, 'category': category})
@login_required
def item_update(request, category_id, pk):
    category = get_object_or_404(Category, pk=category_id)
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list', category_id=category_id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'item_form.html', {'form': form, 'category': category})

@login_required
def item_delete(request, category_id, pk):
    category = get_object_or_404(Category, pk=category_id)
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list', category_id=category_id)
    return render(request, 'item_confirm_delete.html', {'item': item, 'category': category})
