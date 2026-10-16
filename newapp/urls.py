from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('change-password/', views.change_password, name='change-password'),
    path('profile/', views.profile, name='profile'),
    path('shop/<str:cat>/', views.shop, name='shop'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('new-password/', views.new_password, name='new-password'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('seller-add-product/', views.seller_add_product, name='seller-add-product'),
    path('seller-view-product/<str:cat>/', views.seller_view_product, name='seller-view-product'),
    path('seller-edit-product/<int:pk>', views.seller_edit_product, name='seller-edit-product'),
    path('seller-delete-product/<int:pk>', views.seller_delete_product, name='seller-delete-product'),
    path('product-details/<int:pk>', views.product_details, name='product-details'),
    path('add-to-wishlist/<int:pk>', views.add_to_wishlist, name='add-to-wishlist'),
    path('remove-from-wishlist/<int:pk>', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-cart/<int:pk>', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:pk>', views.remove_from_cart, name='remove-from-cart'),
    path('cart/', views.cart, name='cart'),
    path('change-qty/<int:pk>', views.change_qty, name='change-qty'),
    path('create-checkout-session/', views.create_checkout_session, name='payment'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('myorder/', views.myorder, name='myorder'),
]