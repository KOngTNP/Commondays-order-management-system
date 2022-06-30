from django.urls import path
from mysite import views
 
app_name = 'mysite'

urlpatterns = [
    path('tag/<slug:slug>/', views.tagged, name="tagged"),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('product/',views.product, name='product'),
    path('product/detail/<str:product_id>', views.productDetail, name='productDetail'),
    path('product/addProduct/', views.createProduct, name='addProduct'),

    path('table/', views.table, name='table'),
    path('table/addStatement/', views.createStatement, name='addStatement'),
    path('table/delete/<str:statement_id>', views.deleteStatement, name='deleteStatement'),
]