from django.contrib import admin
from .models import Account, Statement, Product, Stock, Order
# Register your models here.
class excludeID(admin.ModelAdmin):
    exclude = ["id"]
admin.site.register(Statement,excludeID)
admin.site.register(Product,excludeID)
admin.site.register(Stock,excludeID)
admin.site.register(Account,excludeID)
admin.site.register(Order,excludeID)
