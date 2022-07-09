from django import forms
from django.contrib.auth.forms import UserCreationForm


from .models import Statement, Product, Stock, Order, Customer, Item
from django.forms import ModelForm

class CreateStatementForm(ModelForm):
    class Meta:
        model = Statement
        fields = "__all__"

class UpdateStatementForm(ModelForm):
    class Meta:
        model = Statement
        fields = ['item','income_amount','outcome_amount','tags']


class CreateProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

class UpdateProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name','description']


class CreateStockForm(ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"

class UpdateStockForm(ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"


class CreateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

class UpdateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = "__all__"


class CreateCustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

class UpdateCustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

class CreateItemForm(ModelForm):
    class Meta:
        model = Item
        fields = "__all__"

class CreateItemForm(ModelForm):
    class Meta:
        model = Item
        fields = "__all__"

class UpdateItemForm(ModelForm):
    class Meta:
        model = Item
        fields = "__all__"