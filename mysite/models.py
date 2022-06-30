from pyexpat import model
import uuid
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase
from django.utils.translation import ugettext_lazy as _

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

class Statement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(null=True)
    item = models.CharField(max_length=150)
    tags = TaggableManager(through=UUIDTaggedItem, blank=False)
    option = models.CharField(max_length=10, choices=option_choices)

    income_amount = models.FloatField(null=True, blank=True)
    outcome_amount = models.FloatField(null=True, blank=True)

    last_balance = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-date','-created_at']
    
    def __str__(self):
        return self.item + " | " + str(self.date)



class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name + " | " + self.description


size_choices = (
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL')
        )

class Stock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=2, choices=size_choices, null=True)
    quantity = models.FloatField(null=True)
    description = models.CharField(max_length=150, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.product.name + " | " + self.description

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    telephone = models.CharField(max_length=10)
    quantity = models.FloatField(null=True)
    date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name + " | " + self.stock.product.name