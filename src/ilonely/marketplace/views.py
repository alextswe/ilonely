from django.shortcuts import render, redirect
from marketplace.models import Product
from django.contrib.auth.models import User
from pages.models import Profile
from django.core.files.storage import FileSystemStorage
from marketplace.forms import ProductForm, EditProduct
from pages.geo import getNearby
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

# Create your views here.
@login_required(login_url="home")
def marketplace(request):
    sellersNearby = getNearby(request.user, 30)
    nearbyProducts = Product.objects.none()
    myProducts = Product.objects.filter(seller=request.user.profile)

    for person in sellersNearby:
        products = Product.objects.filter(seller=person)
        nearbyProducts = nearbyProducts | products

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller= request.user.profile
            product.location = request.user.profile.location
            product.save()
            return redirect('marketplace')
    elif request.method == 'GET':
        if request.GET.get('sortBy', False) and request.GET['sortBy'] != 'None':
            sortByValue = request.GET['sortBy']
            if sortByValue == 'new':
                nearbyProducts = nearbyProducts.order_by('-date_created')
            elif sortByValue == 'lowHigh':
                nearbyProducts = nearbyProducts.order_by('price')
            elif sortByValue == 'highLow':
                nearbyProducts = nearbyProducts.order_by('-price')

        if request.GET.get('minPrice') and request.GET.get('maxPrice'):
            minPrice = request.GET['minPrice']
            maxPrice = request.GET['maxPrice']
            nearbyProducts = nearbyProducts.filter(price__gte=minPrice).filter(price__lte=maxPrice)
        elif request.GET.get('minPrice'):
            minPrice = request.GET['minPrice']
            nearbyProducts = nearbyProducts.filter(price__gte=minPrice)
        elif request.GET.get('maxPrice'):
            maxPrice = request.GET['maxPrice']
            nearbyProducts = nearbyProducts.filter(price__lte=maxPrice)

        if request.GET.get('postedWithin', False) and request.GET['postedWithin'] != 'None':
            postedWithinValue = request.GET['postedWithin']
            print(postedWithinValue)
            if postedWithinValue == '24':
                nearbyProducts = nearbyProducts.filter(date_created__gte=datetime.now()-timedelta(days=1))                
            elif postedWithinValue == '7':
                nearbyProducts = nearbyProducts.filter(date_created__gte=datetime.now()-timedelta(days=7))
            elif postedWithinValue == '30':
                nearbyProducts = nearbyProducts.filter(date_created__gte=datetime.now()-timedelta(days=30))

    nearbyProducts = nearbyProducts.filter(sold=False)
    form = ProductForm()

    return render(
        request,
        'marketplace/marketplace.html',
        {
            'title':'Marketplace',
            'products': nearbyProducts,
            'myProducts': myProducts,
            'form': form,
        }
    )

def listing(request, product_id):
    product = Product.objects.get(pk=product_id)

    return render(
        request,
        'marketplace/listing.html',
        {
            'title': product.name,
            'product': product,
        }
    )

def seller_view(request, product_id):
    product = Product.objects.get(pk=product_id)
    form = EditProduct(instance=product)

    if product.seller.user != request.user:
        return redirect('listing', product_id)

    if request.method == 'POST':
        if not request.POST.get('cancel'):
            form=EditProduct(request.POST, request.FILES, instance=product)
            if form.is_valid():
                product = form.save()

    return render(
        request,
        'marketplace/seller_view.html',
        {
            'title': product.name,
            'product': product,
            'form': form,
        }
    )
