from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('cart/', views.cart, name="cart"),
    path('about/', views.about, name="about"),
    path('checkout/', views.checkout, name="checkout"),
    path('contact', views.contact, name="contact"),
    path('item-detail/', views.itemDetail, name="itemDetail"),
    path('login/', views.loginUser, name="login"),
    path("logout/", views.Logout, name="logout"),
    path('register/', views.registerUser, name="register"),
    path('store/', views.store, name="store"),
	path('add-to-cart/<slug>/',views.add_to_cart, name='add'),
    path('remove-from-cart-page/<slug>/',views.remove_from_cart_page, name='remove-from-cart-page'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path("user-profile/", views.user_profile, name="profile"),
    path("all-orders/", views.all_orders, name="all_orders"),
    path("users/", views.all_users, name="users"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path('item-detail/<str:pk>/', views.item_detail, name='item-detail'),
    path('wishlist/', views.wishlist, name="wishlist"),
    path('add-to-wishlist/<slug>/', views.add_to_wishlist, name='add-to-wishlist')
]