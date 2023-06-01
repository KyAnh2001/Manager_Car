from django.urls import path
from . import views

urlpatterns = [
    # Car
    path('products', views.ProductsView.as_view(), name='car-products'),
    path('productdetail/<pid>', views.ProductDetailView.as_view(), name='car-productdetail'),
    path('orders', views.OrdersView.as_view(), name='car-orders'),
    # path('customers', views.CustomersView.as_view(), name='car-customers'),
    path('cart', views.CartView.as_view(), name='car-cart'),
    path('checkout', views.CheckOutView.as_view(), name='car-checkout'),
    path('shops', views.ShopsView.as_view(), name='car-shops'),
    path('productlist', views.ProductListView.as_view(), name='car-productlist'),
    path('addproduct', views.AddProductView.as_view(), name='car-addproduct'),
    path('editproduct/<pid>', views.EditProductView.as_view(), name='car-editproduct'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path('delete_cart_item/', views.DeleteCartItemView.as_view(), name='delete_cart_item'), # car/delete_cart_item
    path('invoice/<oid>', views.InvoiceView.as_view(), name='car-invoice'),
    path('invoices/', views.InvoiceListView.as_view(), name='car-invoices'),
]
