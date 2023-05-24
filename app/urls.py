from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('cart/', views.cart, name="cart"),
    path('about/', views.about, name="about"),
    path('checkout/', views.checkout, name="checkout"),
    path('contact', views.contact, name="contact"),
    path('login/', views.loginUser, name="login"),
    path("logout/", views.Logout, name="logout"),
    path('register/', views.registerUser, name="register"),
    path('store/', views.store, name="store"),
	path('add-to-cart/<slug>/',views.add_to_cart, name='add'),
    path('remove-from-cart-page/<slug>/',views.remove_from_cart_page, name='remove-from-cart-page'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('item-detail/<str:pk>/', views.item_detail, name='item-detail'),
    path('wishlist/', views.wishlist, name="wishlist"),
    path('add-to-wishlist/<slug>/', views.add_to_wishlist, name='add-to-wishlist'),
    path('payment-completed/', views.payment_completed, name='payment-completed'),
    path('paypal-payment/', views.payment, name="paypal-payment"),
    path('payment-successful/', views.payment_successful, name="payment-successful"),
    path('paypal-failed/', views.payment_unsuccessful, name="payment-failed"),
    path("delete-review/<str:id>/", views.delete_review, name="delete-review"),
    path('remove-from-cart-page/<slug>/',views.remove_from_cart_page, name='remove-from-cart-page'),
    path('remove-item-from-cart-page/<slug>/',views.remove_single_item_from_cart_page, name='remove-single-item-from-cart-page'),
    path('add-item-to-cart-page/<slug>/',views.add_single_item_from_cart_page, name='add-single-item-to-cart-page'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path('item-detail-add-to-cart/<slug>/',views.add_to_cart_item_detail_page, name='add-item-detail'),
	path('item-detail-remove-from-cart/<slug>/',views.remove_from_cart_item_detail_page, name='remove-item-detail'),
    path('order-detail/<str:pk>/', views.orderDetail, name='order-detail')
]