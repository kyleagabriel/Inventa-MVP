from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:pk>/delete/", views.delete_product, name="delete_product"),
    path("po/new/", views.po_create, name="po_create"),
    path("po/<int:pk>/", views.po_detail, name="po_detail"),
    path("po/<int:pk>/confirm/", views.po_confirm, name="po_confirm"),
]
