from django.contrib import admin
from .models import Account, Statement, Product, Stock,Customer, Order, Item
# Register your models here.
class excludeID(admin.ModelAdmin):
    exclude = ["id"]
admin.site.register(Statement,excludeID)
admin.site.register(Product,excludeID)
admin.site.register(Stock,excludeID)
admin.site.register(Account,excludeID)
admin.site.register(Customer,excludeID)
admin.site.register(Order,excludeID)
admin.site.register(Item,excludeID)
