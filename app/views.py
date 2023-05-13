from django.shortcuts import render
from .forms import *
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages
import re
from django.core.exceptions import ObjectDoesNotExist
import random,string
import operator
from collections import Counter
from .utils import *

# Create your views here.

def home(request):
	new_arrival = Item.objects.all().order_by('-id')[:8]
	hot_sales = get_hot_sales()
	wishlist = Wishlist.objects.filter(user=request.user).first().items.all() if Wishlist.objects.filter(user=request.user).exists() else []
	context = { 'new_arrival':new_arrival, 'hot_sales':hot_sales, 'wishlist':wishlist}

	return render(request,'app/home.html',context)

@login_required(login_url="/login")
def cart(request):
	try:
		order = Order.objects.get(user=request.user, ordered=False)
		context = {'order':order}
		return render(request, 'app/cart.html', context)
	except ObjectDoesNotExist:
		messages.info(request, "You do not have an active Order")
		return redirect("store")

@login_required(login_url="/login")
def Logout(request):
	logout(request)
	messages.success(request, "We hope to see you soon")
	return redirect("home")

def loginUser(request):
	if request.user.is_authenticated:
		return redirect('home')
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, "You signed in as " + user.username)
			return redirect("home")
		else:
			messages.info(request, "Invalid details provided")
			return redirect("login")
	context = {}
	return render(request,'app/login.html',context)

def registerUser(request):
	if request.user.is_authenticated:
		return redirect('home')
	user_form = RegisterUserForm()
	if request.method == "POST":
		user_form = RegisterUserForm(request.POST)
		if user_form.is_valid():
			try:
				user_form.save()
				messages.success(request, "Your account was successfully created")
				return redirect("login")
			except Exception as e:
				messages.error(request,"" + type(e))
				return redirect("register")
	context = {'user_form':user_form}
	return render(request,'app/login.html',context)

def about(request):
	context = {}
	return render(request,'app/about.html',context)

def store(request):
	items = Item.objects.all()
	categories = Category.objects.all()
	brands = Brand.objects.all()
	colors = ItemColor.objects.all()
	sizes = Size.objects.all()
	wishlist = Wishlist.objects.filter(user=request.user).first().items.all() if Wishlist.objects.filter(user=request.user).exists() else []
	context = {'items':items, 'categories':categories, 'brands':brands, 'sizes':sizes, 'colors':colors, 'wishlist':wishlist}
	return render(request,'app/store.html',context)

def itemDetail(request):
	context = {}
	return render(request,'app/item-detail.html',context)

@login_required(login_url="/login")
def checkout(request):
	order = get_object_or_404(Order, user=request.user, ordered=False)
	form = CheckoutForm()
	context = {'order':order, 'form':form}
	shipping_address_qs = Address.objects.filter(
		user = request.user,
		default = True,)
	if shipping_address_qs.exists():
		context.update({'default_delivery_address':shipping_address_qs[0]})
	
	if request.method == "POST":
		form = CheckoutForm(request.POST or None)
		order = get_object_or_404(Order, user=request.user, ordered=False)
		if form.is_valid():
			use_default_delivery = form.cleaned_data.get('use_default_delivery')
			if use_default_delivery:
				address_qs = Address.objects.filter(user=request.user, default=True)
				if address_qs.exists():
					shipping_address = address_qs[0]
					order.full_name = shipping_address.full_name
					order.city = shipping_address.city
					order.house_address = shipping_address.house_address
					order.country = shipping_address.country
					order.postal_code = shipping_address.postal_code
					order.phone = shipping_address.phone
					order.order_notes = form.cleaned_data.get("order_notes")
					order_items = order.items.all()
					order_items.update(ordered=True)
					for item in order_items:
						item.save()
					order.ordered = True
					order.status = "processing"
					order.ref_code = create_ref_code()
					order.save()
					messages.success(request, "Your Order has been successfully created")
					return redirect("/")
				else:
					messages.error(request, "You do not have a default address")
					return redirect('checkout')
			else:
				full_name = form.cleaned_data.get('full_name')
				city = form.cleaned_data.get('city')
				house_address = form.cleaned_data.get('house_address')
				country = form.cleaned_data.get('country')
				postal_code = form.cleaned_data.get('postal_code')
				phone = form.cleaned_data.get('phone')
				order_notes = form.cleaned_data.get('order_notes')
				arr  = [full_name,city,house_address,country,postal_code,phone]

				if is_valid_form(arr):
					shipping_address = Address(
							user=request.user,
							full_name=full_name,
							city=city,
							house_address=house_address,
							country=country,
							postal_code=postal_code,
							phone=phone
					)
					order.full_name = shipping_address.full_name
					order.city = shipping_address.city
					order.house_address = shipping_address.house_address
					order.country = shipping_address.country
					order.postal_code = shipping_address.country
					order.phone = shipping_address.phone
					order.order_notes = order_notes
					order.save()
					set_default_delivery = form.cleaned_data.get('set_default_delivery')
					if set_default_delivery:
						try:
							old_default_address = Address.objects.filter(user=request.user, default=True).update(default=False)
							shipping_address.default = True
							shipping_address.save()
						except ObjectDoesNotExist:
							shipping_address.default = True
							shipping_address.save()
					order_items = order.items.all()
					order_items.update(ordered=True)
					for item in order_items:
						item.save()
					order.ordered = True
					order.status = "processing"
					order.ref_code = create_ref_code()
					order.save()
					messages.success(request, "Your Order was successfull")
					return redirect("/")
		else:
			messages.info(request, "Please fill in valid details")
			return redirect("checkout")
	return render(request,'app/checkout.html',context)

def contact(request):
	if request.method == "POST":
		try:
			name = request.POST.get('full_name')
			email = request.POST.get('email')
			message = request.POST.get('message')
			print(name, email, message)
			contact = Contact(full_name=name, email=email, message=message)
			contact.save()
			messages.success(request, "Thank you for contacting Aurora, We will get back to you shortly!")
			return redirect('contact')
		except Exception as e:
			messages.error(request, e)
			return redirect('contact')
	context = {}
	return render(request,'app/contact.html',context)

@login_required(login_url="/login")
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request,"This item quantity was updated")
			return redirect("store")
		else:
			order.items.add(order_item)
			messages.info(request,"This item was added to cart")
			return redirect('store')
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request,"This item was added to cart")
	return redirect('store')



@login_required(login_url="/login")
def remove_from_cart_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			order_item.delete()
			messages.info(request, "This item was removed from your cart.")
			return redirect("cart")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("cart")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("cart")
	 

@login_required(login_url="/login")
def dashboard(request):
	sales = Order.objects.filter(status="delivered").count()
	orders_delivered = Order.objects.filter(status="delivered")
	recent_orders = Order.objects.filter(ordered = True).order_by('-ordered_date')[0:6]
	customers = User.objects.count()
	most_popular_items = get_popular_items()
	revenue = 0
	for order in orders_delivered:
		revenue += order.get_total()
	context = {'sales':sales, 'revenue':revenue, 'customers':customers, 
		'recent_orders':recent_orders, 'most_popular_items' : most_popular_items}
	return render(request, "app/dash/dash.html", context)


@login_required(login_url="/login")
def user_profile(request):
	context = {}
	return render(request, "app/dash/user-profile.html", context)

@login_required(login_url="/login")
def all_orders(request):
	orders = Order.objects.filter(ordered = True)
	sales = Order.objects.filter(status="delivered").count()
	orders_delivered = Order.objects.filter(status='delivered')
	customers = User.objects.count()
	revenue = 0
	for order in orders_delivered:
		revenue += order.get_total()
	context = {'orders':orders, 'orders_delivered':orders_delivered, 'sales':sales, 'revenue':revenue, 'customers':customers}
	return render(request, "app/dash/all-orders.html", context)

@login_required(login_url="/login")
def all_users(request):
	users = User.objects.all()
	sales = Order.objects.filter(status="delivered").count()
	orders_delivered = Order.objects.filter(status="delivered")
	customers = User.objects.count()
	revenue = 0
	for order in orders_delivered:
		revenue += order.get_total()
	context = {'users':users, 'orders_delivered':orders_delivered, 'sales':sales, 'revenue':revenue, 'customers':customers}
	return render(request, "app/dash/users.html", context)


@login_required(login_url="/login")
def my_orders(request):
	orders = Order.objects.filter(ordered = True, user=request.user)
	sales = Order.objects.filter(status="delivered").count()
	orders_delivered = Order.objects.filter(status="delivered")
	my_order = True
	customers = User.objects.count()
	revenue = 0
	for order in orders_delivered:
		revenue += order.get_total()
	context = {'orders':orders, 'orders_delivered':orders_delivered, 'sales':sales, 'revenue':revenue,
	     'customers':customers, 'my_order':my_order}
	return render(request, "app/dash/all-orders.html", context)


def item_detail(request, pk):
	item = get_object_or_404(Item,id=pk)
	reviews = Review.objects.filter(item=item)
	related = Item.objects.filter(category__in=item.category.all()).exclude(id=item.id)[0:4]
	# user_review = check_user_review(request.user, item)
	# redirect_path = request.META.get('HTTP_REFERER', reverse('home'))

	context = {'item':item, 'reviews':reviews, 'related':related}
	return render(request, 'app/item-detail.html', context)


@login_required(login_url="/login")
def add_to_wishlist(request, slug):
	item = get_object_or_404(Item, slug=slug)
	wishlist_qs = Wishlist.objects.filter(user=request.user)
	if wishlist_qs.exists():
		wishlist = wishlist_qs[0]
		if wishlist.items.filter(slug=item.slug).exists():
			messages.info(request,"This item was removed from your wishlist")
			wishlist.items.remove(item)
			wishlist.save()
		else:
			wishlist.items.add(item)
			wishlist.save()
			messages.success(request,"This item was added to your wishlist")
	else:
		wishlist = Wishlist.objects.create(user=request.user)
		wishlist.items.add(item)
		wishlist.save()
		messages.success(request,"This item was added to your wishlist")
	return redirect(request.META.get('HTTP_REFERER', reverse('store')))

@login_required(login_url="/login")
def wishlist(request):
	wishlist = Wishlist.objects.filter(user=request.user)[0]
	context = {'wishlist':wishlist}
	return render(request,'app/wishlist.html', context)