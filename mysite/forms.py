from django import forms
from django.contrib.auth.forms import UserCreationForm


from .models import Statement, Product
from django.forms import ModelForm

class CreateStatementForm(ModelForm):
    class Meta:
        model = Statement
        fields = "__all__"

class CreateProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"