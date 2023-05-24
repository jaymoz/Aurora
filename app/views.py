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
import json
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode
import time
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

def home(request):
	new_arrival = Item.objects.all().order_by('-id')[:8]
	hot_sales = get_hot_sales()
	context = { 'new_arrival':new_arrival, 'hot_sales':hot_sales}
	if request.user.is_authenticated:
		wishlist = Wishlist.objects.filter(user=request.user).first().items.all() if Wishlist.objects.filter(user=request.user).exists() else []
		context.update({'wishlist':wishlist})
	
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
			email = user_form.cleaned_data['email']
			if User.objects.filter(email=email).exists():
				messages.error(request, "Email already exists. Please use a different email.")
				return redirect("register")
			try:
				user_form.save()
				messages.success(request, "Your account was successfully created")
				return redirect("login")
			except Exception as e:
				messages.error(request, str(type(e)))
				return redirect("register")
		else:
			messages.warning(request, user_form.errors)

	context = {'user_form': user_form}
	return render(request, 'app/login.html', context)

def about(request):
	context = {}
	return render(request,'app/about.html',context)

def store(request):
	items = Item.objects.all()
	categories = Category.objects.all()
	brands = Brand.objects.all()
	colors = ItemColor.objects.all()
	sizes = Size.objects.all()
	paginator = Paginator(items, 12)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)

	context = {
		'items': paginated_queryset,
		'categories': categories,
		'brands': brands,
		'sizes': sizes,
		'colors': colors,
		'page_request_var': page_request_var
	}

	if request.user.is_authenticated:
		wishlist = Wishlist.objects.filter(user=request.user).first().items.all() if Wishlist.objects.filter(
			user=request.user).exists() else []
		context.update({'wishlist': wishlist})

	if request.method == 'GET':
		selected_categories = request.GET.getlist('category_name')
		selected_brands = request.GET.getlist('brand_name')
		selected_sizes = request.GET.getlist('size_name')
		selected_colors = request.GET.getlist('color_name')

		if request.GET.get('min-price') and request.GET.get('max-price'):
			min_price = float(request.GET.get('min-price'))
			max_price = float(request.GET.get('max-price'))
			print(min_price, " : ", max_price)

		if selected_categories:
			items = items.filter(category__name__in=selected_categories)

		if selected_brands:
			items = items.filter(brand__name__in=selected_brands)

		if selected_sizes:
			items = items.filter(size__size__in=selected_sizes)

		if selected_colors:
			items = items.filter(color__color__in=selected_colors)

		if request.GET.get('min-price') and request.GET.get('max-price'):
			items = items.filter(price__gte=min_price, price__lte=max_price)

		# Update the pagination after applying filters
		paginator = Paginator(items, 12)
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)

	context['items'] = paginated_queryset
	return render(request, 'app/store.html', context)



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
			use_default_delivery = form.cleaned_data.get('use_default_address')
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
					order.order_notes = form.cleaned_data.get('order_notes')
					order.save()
					return redirect('paypal-payment')
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
					return redirect("paypal-payment")
				else:
					messages.warning(request, "Please fill all form fields")
					return redirect("checkout")
		else:
			messages.info(request, "Please fill in valid details")
			return redirect("checkout")
	return render(request,'app/checkout.html',context)

@login_required(login_url="/login")
def payment(request):
	order = get_object_or_404(Order, user=request.user, ordered=False)
	context = {'order':order}
	return render(request, "app/payment.html", context)

@login_required(login_url="/login")
def payment_completed(request):
	if request.method == 'POST':
		body = json.loads(request.body)
		order = get_object_or_404(Order, id=body["orderId"])
		status = body["status"]
		if status.lower() == "completed":
			order_items = order.items.all()
			order_items.update(ordered=True)
			for item in order_items:
				item.save()
			order.ordered = True
			order.status = "processing"
			order.ref_code = create_ref_code()
			order.save()
			# Redirect to the payment completed page
			return redirect('payment-successful')
		else:
			# Redirect to the payment not complete page
			return redirect('payment-failed')
	else:
		# Return a bad request response if the request is not a POST request
		return HttpResponseBadRequest()

@login_required(login_url="/login")
def payment_successful(request):
	return render(request, "app/payment-successful.html")

@login_required(login_url="/login")
def payment_unsuccessful(request):
	return render(request, "app/payment-unsuccessful.html")

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
			messages.success(request,"This item was added to cart")
			return redirect('store')
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.success(request,"This item was added to cart")
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

@login_required
def add_single_item_from_cart_page(request, slug):
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
			return redirect("cart")
		else:
			order.items.add(order_item)
			messages.info(request,"This item was added to cart")
			return redirect('cart')
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request,"This item quantity was updated")
	return redirect('cart')

@login_required
def remove_single_item_from_cart_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This item quantity was updated.")
			return redirect("cart")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("cart")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("cart")

@login_required
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
			if order_item.item.slug == "delivery":
				order.items.remove(order_item)
				order_item.delete()
				messages.info(request, "Delivery has been removed from this order")
				return redirect("cart")
			else:
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

@login_required
def add_to_cart_item_detail_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			if order_item.item.slug == "delivery":
				order_item.quantity = 1
				order_item.save()
				messages.info(request, "You can only add a delivery fee per order")
				return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
			else:
				order_item.quantity += 1
				order_item.save()
				messages.info(request,"This item quantity was updated")
				return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
		else:
			order.items.add(order_item)
			messages.success(request,"This item was added to cart")
			return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
	
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.success(request,"This item was added to cart")
	return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

@login_required
def remove_from_cart_item_detail_page(request, slug):
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
			messages.success(request, "This item was removed from your cart.")
			return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
		else:
			messages.info(request, "This item was not in your cart")
			return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
	else:
		messages.info(request, "You do not have an active order")
		return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

@login_required(login_url="/login")
def dashboard(request):
	recent_orders = Order.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	most_popular_items = get_popular_items()
	context = {'recent_orders':recent_orders, 'most_popular_items' : most_popular_items}
	return render(request, "app/dash/dash.html", context)

@login_required(login_url="/login")
def orderDetail(request, pk):
	order = get_object_or_404(Order, id=pk)
	context = {'order':order}
	return render(request, "app/dash/order-detail.html", context)

def item_detail(request, pk):
	item = get_object_or_404(Item,id=pk)
	reviews = Review.objects.filter(item=item)
	related = Item.objects.filter(category__in=item.category.all()).exclude(id=item.id)[0:4]
	user_review = check_user_review(request.user, item)
	redirect_path = request.META.get('HTTP_REFERER', reverse('home'))
	if request.method == "POST":
		comment = request.POST.get('message')
		rating = request.POST.get('rating')
		if comment and rating:
			review = Review.objects.create(
				user=request.user,
				item=item,
				comment=comment,
				rating=rating,
			)
			review.save()
			messages.success(request, "Your review was successfully submitted")
			return redirect(redirect_path)

	context = {'item':item, 'reviews':reviews, 'related':related, 'user_review':user_review}
	if request.user.is_authenticated:
		wishlist = Wishlist.objects.filter(user=request.user).first().items.all() if Wishlist.objects.filter(user=request.user).exists() else []
		context.update({'wishlist':wishlist})
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

@login_required
def delete_review(request, id):
	review = get_object_or_404(Review, id=id)
	redirect_path = request.META.get('HTTP_REFERER', reverse('home'))
	review.delete()
	messages.success(request, "Your review was deleted")
	return redirect(redirect_path)


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "app/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Aurora',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'aurora@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
			else:
				messages.warning(request, "This email is not registered on this website")
		else:
			messages.error(request, password_reset_form.errors)
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="app/password/password_reset.html", context={"password_reset_form":password_reset_form})