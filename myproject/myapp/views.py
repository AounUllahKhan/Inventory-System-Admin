from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import UserRegisterForm
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin

class Index(TemplateView):
	template_name = 'index.html'
     
class SignUpView(View):
	def get(self, request):
		form = UserRegisterForm()
		return render(request, 'signup.html', {'form': form})

	def post(self, request):
		form = UserRegisterForm(request.POST)

		if form.is_valid():
			form.save()
			user = authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password1']
			)

			login(request, user)
			return redirect('index')

		return render(request, 'signup.html', {'form': form})


class Dashboard(LoginRequiredMixin, View):
	def get(self, request):
		return render(request, 'dashboard.html')
     
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@require_POST
def user_logout(request):
    logout(request)
    return render(request, 'logout.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Item
from .forms import CategoryForm, ItemForm

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form=CategoryForm(data=request.POST,files=request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category,files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category, files=request.FILES)
    return render(request, 'category_form.html', {'form': form})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})

@login_required
def item_list(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    items = Item.objects.filter(category=category)
    alert = any(item.quantity < 25 for item in items)
    return render(request, 'item_list.html', {'category': category, 'items': items, 'alert': alert})

@login_required
def item_create(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, files=request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = category
            item.save()
            return redirect('item_list',category_id=category.id)
        
    else:
        form = ItemForm()
    return render(request, 'item_form.html', {'form': form, 'category': category})


@login_required
def item_update(request, category_id, pk):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    item = get_object_or_404(Item, pk=pk, category=category)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('item_list', category_id=category.id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'item_form.html', {'form': form, 'category': category})


@login_required
def item_delete(request, category_id, pk):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    item = get_object_or_404(Item, pk=pk, category=category)
    print("Item to delete:", item)  # Debugging statement
    if request.method == 'POST':
        print("Received POST request")  # Debugging statement
        item.delete()
        print("Item deleted successfully")  # Debugging statement
        return redirect('item_list', category_id=category.id)
    return render(request, 'item_confirm_delete.html', {'item': item, 'category': category})