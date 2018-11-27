from django.conf.urls import include, url
from django.urls import path, include
from django.contrib.auth import views
import marketplace.views

urlpatterns = [
    path('', marketplace.views.marketplace, name='marketplace'),
    path('listing/<int:product_id>/', marketplace.views.listing, name='listing'),
    path('seller_view/<int:product_id>/', marketplace.views.seller_view, name='seller_view'),
]
