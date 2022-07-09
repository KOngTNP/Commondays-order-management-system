from django.urls import path
from mysite import views
 
app_name = 'mysite'

urlpatterns = [
    path('tag/<slug:slug>/', views.tagged, name="tagged"),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('product/',views.product, name='product'),
    path('product/detail/<str:product_id>', views.productDetail, name='productDetail'),

    path('product/detail/<str:product_id>/createStock', views.createStock, name='createStock'),
    path('product/detail/<str:product_id>/edit/<str:stock_id>', views.editStock, name='createStock'),
    path('product/detail/<str:product_id>/update/<str:stock_id>', views.updateStock, name='createStock'),

    path('order/', views.order, name='order'),

    path('order/createOrder', views.createOrder, name='createOrder'),
    path('order/edit/<str:order_id>', views.editOrder, name='editOrder'),
    path('order/update/<str:order_id>', views.updateOrder, name='updateOrder'),
    path('order/<str:order_id>/item', views.createItem, name='createItem'),
    path('order/<str:order_id>/item/edit/<str:item_id>', views.editItem, name='editItem'),
    path('order/<str:order_id>/item/delete/<str:item_id>', views.deleteItem, name='deleteItem'),

    path('product/addProduct/', views.createProduct, name='addProduct'),
    path('product/edit/<str:product_id>', views.editProduct, name='editProduct'),
    path('product/update/<str:product_id>', views.updateProduct, name='updateProduct'),
    # path('product/delete/<str:product_id>', views.deleteProduct, name='deleteProduct'),

    path('table/<str:account_id>/', views.table, name='table'),
    path('table/', views.get_table, name='get_table'),
    path('table/<str:account_id>/addStatement', views.createStatement, name='addStatement'),
    path('table/<str:account_id>/delete/<str:statement_id>', views.deleteStatement, name='deleteStatement'),
    path('table/<str:account_id>/edit/<str:statement_id>', views.editStatement, name='editStatement'),
    path('table/<str:account_id>/update/<str:statement_id>', views.updateStatement, name='updateStatement'),

    path('CreateCustomer/', views.create_customer, name='create_customer'),
]