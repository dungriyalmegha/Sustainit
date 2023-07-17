from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, UserProfile, Transaction, ShippingAddress, Order
from .forms import ProductForm, UserProfileForm, ShippingAddressForm, OrderForm


from django.contrib.auth.forms import UserCreationForm


from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import login


def index(request):
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-created_at')[:6]
    context = {'categories': categories, 'products': products}
    return render(request, 'index.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Your product has been listed.')
            return redirect('product_detail', product.pk)
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your product has been updated.')
            return redirect('product_detail', product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})

def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def buy_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        coins = int(request.POST.get('coins'))
        if request.user.userprofile.coins >= coins:
            transaction = Transaction.objects.create(
                buyer=request.user,
                product=product,
                coins=coins,
            )
            request.user.userprofile.coins -= coins
            request.user.userprofile.save()
            product.seller.userprofile.coins += coins
            product.seller.userprofile.save()
            messages.success(request, f"You have bought {product.name} for {coins} coins.")
            return redirect('product_detail', pk)
        else:
            messages.error(request, 'You do not have enough coins to buy this product.')
    return render(request, 'buy_product.html', {'product': product})

@login_required
def add_shipping_address(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Your shipping address has been saved.')
            return redirect('checkout')
    else:
        form = ShippingAddressForm()
    return render(request, 'add_shipping_address.html', {'form': form})


@login_required
def checkout(request):
    if request.method == 'POST':
        product_id = request.POST['product']
        product = get_object_or_404(Product, pk=product_id)
        coins = int(request.POST['coins'])
        shipping_address_id = request.POST['shipping_address']
        shipping_address = get_object_or_404(ShippingAddress, pk=shipping_address_id)
        if coins <= request.user.userprofile.coins:
            Order.objects.create(buyer=request.user, product=product, coins=coins, shipping_address=shipping_address)
            request.user.userprofile.coins -= coins
            request.user.userprofile.save()
            product.seller.userprofile.coins += coins
            product.seller.userprofile.save()
            messages.success(request, 'Order placed successfully!')
            return redirect('checkout')

        messages.error(request, 'You do not have enough coins to place this order.')
        return redirect('checkout')

    user_profile = request.user.userprofile
    addresses = ShippingAddress.objects.filter(user=request.user)
    products = Product.objects.filter(seller=request.user)
    orders = Order.objects.filter(product__seller=request.user)
    return render(request, 'checkout.html', {'user_profile': user_profile, 'addresses': addresses, 'products': products, 'orders': orders})



    # views.py



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration.html', {'form': form})






def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Replace 'home' with the actual URL name of your home page
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
