from django.shortcuts import render, redirect
from marketplace.models import Product
from django.contrib.auth.models import User
from pages.models import Profile
from django.core.files.storage import FileSystemStorage
from marketplace.forms import ProductForm

# Create your views here.
def marketplace(request):
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid:
            product = form.save(commit=False)
            product.seller= request.user.profile
            product.location = request.user.profile.location
            product.save()
            return redirect('marketplace')
    else:
        form = ProductForm()

    return render(
        request,
        'marketplace/marketplace.html',
        {
            'title':'Marketplace',
            'products': products,
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
