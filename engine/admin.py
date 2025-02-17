from django.contrib import admin
from . import models


@admin.register(models.Product)
class Product(admin.ModelAdmin):
    list_display = (
        'id', 'uuid', 'user', 'name', 'description', 'count', 'price', 'photo1',
        'photo2', 'photo3', 'photo4', 'photo5', 'photo6', 'created_at',
        'updated_at'
    )


@admin.register(models.OrderProduct)
class OrderProduct(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'count')


@admin.register(models.Order)
class Order(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'user', 'products_display', 'total_cost', 'status', 'created_at')

    def products_display(self, obj):
        return ', '.join([product.name for product in obj.products.all()])

    products_display.short_description = 'products'


@admin.register(models.Address)
class Address(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'location', 'first_name', 'last_name', 'address_line_1',
        'address_line_2', 'country', 'city', 'state', 'zipcode', 'phone_number', 'description'
    )


@admin.register(models.Question)
class Question(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'message')


@admin.register(models.Visit)
class Visit(admin.ModelAdmin):
    list_display = ('id', 'product', 'ip', 'created_at')
    list_filter = ('created_at',)

@admin.register(models.Support)
class Support(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at')
