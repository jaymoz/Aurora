from unicodedata import lookup
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,timedelta
from django.shortcuts import reverse
from multiselectfield import MultiSelectField
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.validators import RegexValidator
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from django.utils import timezone

User = get_user_model()

class Brand(models.Model):
	name = models.CharField(max_length=100)
	class Meta:
		verbose_name_plural = "Brands"
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = 'Brand'

class ItemColor(models.Model):
	color = models.CharField(max_length=100)
	class Meta:
		db_table = "ItemColor"
		verbose_name_plural = "Item Color"

	
	def __str__(self):
		return self.color


class Size(models.Model):
	size = models.CharField(max_length=5)
	class Meta:
		db_table = "Size"
		verbose_name_plural = "Size"
	
	def __str__(self):
		return self.size

class Category(models.Model):
	name = models.CharField(max_length=100)

	class Meta:
		db_table  = "Category"
		verbose_name_plural = 'Categories'
	
	def __str__(self):
		return self.name
	
class Item(models.Model):
	name = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=7, decimal_places=2)
	discount_price = models.DecimalField(max_digits=7, decimal_places=2,blank=True, null=True)
	description = models.TextField(null=True, blank=True)
	category = models.ManyToManyField(Category)
	size = models.ForeignKey(Size, blank=True, null=True, on_delete=models.CASCADE)
	color = models.ManyToManyField(ItemColor)
	brand = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.CASCADE)
	out_of_stock = models.BooleanField(default=False)
	slug = models.SlugField()

	def __str__(self):
		return self.name

	def get_average_rating(self):
		average_rating = Review.objects.filter(item=self).aggregate(Avg('rating'))['rating__avg']
		return average_rating

	def get_absolute_url(self):
		return reverse('store',kwargs={
		'slug':self.slug
		})

	def get_add_to_cart_url(self):
			return reverse('add',kwargs={
			'slug':self.slug
			})
	def get_add_to_wishlist_url(self):
			return reverse('add-to-wishlist',kwargs={
			'slug':self.slug
			})

	def get_remove_from_cart_url(self):
		return reverse('remove',kwargs={
			'slug':self.slug
			})
	
	def get_review_count(self):
		review_count = Review.objects.filter(item=self).count()
		return review_count

	class Meta:
		db_table  = "Item"

class OrderItem(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.quantity}x  {self.item.name}"

	def get_total_item_price(self):
		return self.quantity * self.item.price

	def get_total_discount_item_price(self):
		return self.quantity * self.item.discount_price

	def get_amount_saved(self):
		return self.get_total_item_price() - self.get_total_discount_item_price()

	def get_final_price(self):
		if self.item.discount_price:
			return self.get_total_discount_item_price()
		else:
			return self.get_total_item_price()
		
	class Meta:
		db_table  = "OrderItem"


class Order(models.Model):
	STATUS_CHOICES = (
		('processing','Processing'),
		('on delivery', 'On delivery'),
		('delivered', 'Delivered'),
		('refund requested', 'Refund requested'),
		('refund declined','Refund declined'),
		('refund granted', 'Refund granted'),
		('refund completed', 'Refund completed'),
		('cancelled', 'Cancelled'),

	)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20,blank=True, null=True)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	status = models.CharField(max_length=100, choices=STATUS_CHOICES, blank=True, null=True)
	order_notes = models.CharField(max_length=200, blank=True, null=True)
	full_name = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	house_address = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	postal_code = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)
	
	def __str__(self):
		return str(self.id)

	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return total

	def set_order_status(self, val):
		status_dict = {x[1]:x[0] for x in self.STATUS_CHOICES}
		self.status = status_dict[val]

	class Meta:
		db_table  = "Order"


class Contact(models.Model):
	full_name = models.CharField(max_length=100)
	email = models.EmailField()
	message = models.TextField()
	read = models.BooleanField(default=False)
	def __str__(self):
		return self.email

	class Meta:
		db_table  = "Contact"
	

class Address(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	full_name = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	house_address = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	postal_code = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)
	default = models.BooleanField(default=False)

	class Meta:
		db_table = "Address"
		verbose_name_plural = 'Addresses'

	def __str__(self):
		return (self.house_address)
	

class Review(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	comment = models.TextField(max_length=500)
	rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.item.name

	class Meta:
		db_table  = "Review"
	

class Wishlist(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	items = models.ManyToManyField(Item)
	
	def __str__(self):
		return str(self.id)
	
	class Meta:
		db_table  = "Wishlist"
	

class ItemImage(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	image = models.ImageField(null=True, blank=True)

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url
	
	def __str__(self):
		return self.item.name

	class Meta:
		db_table  = "ItemImage"




