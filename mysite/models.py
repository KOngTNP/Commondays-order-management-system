from pyexpat import model
import uuid
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    balance = models.FloatField(default=0)
    all_income = models.FloatField(default=0)
    all_outcome = models.FloatField(default=0)
    def __str__(self):
        return self.name

class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

option_choices = (
        ('income', 'income'),
        ('outcome', 'outcome')
        )



class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, null=True, blank=True)

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name + " | " + self.description


size_choices = (
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('F', 'F')
        )

class Stock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=2, choices=size_choices, null=True)
    quantity = models.FloatField(null=True)
    description = models.CharField(max_length=150, null=True, blank=True)

    price = models.FloatField()

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.product.name + ", " + self.color + ", " + self.size + " | " + str(self.quantity)



class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    telephone = models.CharField(max_length=10)

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name + ' | ' + self.telephone

platform_choices = (
        ('Shopee,Lazada', 'Shopee,Lazada'),
        ('Other', 'Other')
        )

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date = models.DateField(null=True)
    platform = models.CharField(max_length=13, choices=platform_choices, null=True)
    sum_price = models.FloatField(null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.customer.name + self.customer.telephone + " | " + str(self.date)


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

    price = models.FloatField(blank=True, null=True, default="")

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


    def total_price(self):
        if self.price:
            return self.quantity * self.price
        else:
            return ""

    def __str__(self):
        return self.order.customer.name + ' | ' + self.stock.product.name


class Statement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(null=True)
    item = models.CharField(max_length=150)
    tags = TaggableManager(through=UUIDTaggedItem, blank=False)
    option = models.CharField(max_length=10, choices=option_choices)
    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    income_amount = models.FloatField(null=True, blank=True)
    outcome_amount = models.FloatField(null=True, blank=True)

    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    last_balance = models.FloatField(null=True, blank=True)

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-date','-created_at']
    
    def __str__(self):
        return self.item + " | " + str(self.date)
