from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
import os
from django.conf import settings
from core.utils import generate_presigned_url


def uuid():
    import uuid
    return uuid.uuid4().hex


BUKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
AWS_REGION = settings.AWS_S3_REGION_NAME
AWS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET = settings.AWS_SECRET_ACCESS_KEY


class Product(models.Model):
    uuid = models.CharField(default=uuid, max_length=64, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    count = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo1 = models.FileField(upload_to='products/', blank=True, null=True, max_length=512)
    photo2 = models.FileField(upload_to='products/', blank=True, null=True, max_length=512)
    photo3 = models.FileField(upload_to='products/', blank=True, null=True, max_length=512)
    photo4 = models.FileField(upload_to='products/', blank=True, null=True, max_length=512)
    photo5 = models.FileField(upload_to='products/', blank=True, null=True, max_length=512)
    photo6 = models.FileField(upload_to='products/', blank=True, null=True, max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def pictures(self):
        photo_urls = []
        for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photo6']:
            photo = getattr(self, field)
            if photo:
                photo_urls.append(photo.url)
        return photo_urls

    @property
    def media_items(self):
        items = []
        fields = ['photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photo6']
        for field in fields:
            photo = getattr(self, field)
            if photo:
                # url = photo.url
                object_key = photo.name
                url = generate_presigned_url(BUKET_NAME, object_key)
                path = url.split('?')[0]
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    media_type = 'image'
                elif path.lower().endswith(('.mp4', '.mov', '.avi')):
                    media_type = 'video'
                else:
                    media_type = 'unknown'
                items.append((url, media_type))
        return items

    @property
    def data_img(self):
        if self.photo1:
            object_key = self.photo1.name
            url = generate_presigned_url(BUKET_NAME, object_key)
            return url
        return ''

    @property
    def media_type(self):
        if not self.pictures:
            return 'unknown'

        url = self.pictures[0].lower()
        if url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            return 'image'
        elif url.endswith(('.mp4', '.mov', '.avi')):
            return 'video'
        return 'unknown'

    def serialize(self, order=None) -> dict:
        count = self.count
        if order:
            try:
                order_product = OrderProduct.objects.get(order=order, product=self)
                count = order_product.count
            except OrderProduct.DoesNotExist:
                pass

        return dict(
            user=self.user.id,
            name=self.name,
            description=self.description,
            count=count,
            price=float(self.price),
            photo1=self.data_img,
            media_type=self.media_type,
            product_id=self.id,
        )

    def delete(self, *args, **kwargs):
        for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photo6']:
            photo = getattr(self, field)
            if photo:
                # photo_path = os.path.join(settings.MEDIA_ROOT, photo.name)
                # if os.path.exists(photo_path):
                #     os.remove(photo_path)
                # del S3
                photo.storage.delete(photo.name)

        super().delete(*args, **kwargs)


class OrderProduct(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)


class Order(models.Model):
    CREATED = 1
    PROCESSING = 2
    PAID = 3
    ACCEPTED = 4
    DELIVERING = 5
    DELIVERED = 6
    CANCELED = 7
    REJECTED = 8
    STATUS = (
        (CREATED, 'created'), (PROCESSING, 'processing'), (PAID, 'paid'),
        (ACCEPTED, 'accepted'), (DELIVERING, 'delivering'), (DELIVERED, 'delivered'),
        (CANCELED, 'cancelled'), (REJECTED, 'rejected')
    )

    uuid = models.CharField(default=uuid, max_length=64, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True, through=OrderProduct)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    location = models.CharField(max_length=128, blank=True, default='In stock')
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    address_line_1 = models.CharField(max_length=128, blank=True)
    address_line_2 = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=64, blank=True)
    state = models.CharField(max_length=64, blank=True)
    zipcode = models.CharField(max_length=64, blank=True)
    phone_number = models.CharField(default='', max_length=16,blank=True)
    description = models.TextField(blank=True)
    status = models.IntegerField(choices=STATUS, default=CREATED)
    current_location = models.CharField(max_length=64, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def update_costs(self):
        self.total_cost = sum(
            order_prod.product.price * order_prod.count for order_prod in OrderProduct.objects.filter(order=self))
        self.save()


@receiver(m2m_changed, sender=Order.products.through)
def update_total_cost(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.total_cost = sum(product.price for product in instance.products.all())
        instance.save()


@receiver(post_save, sender=Order)
def update_total_cost_on_create(sender, instance, created, **kwargs):
    if created:
        instance.total_cost = sum(product.price for product in instance.products.all())
        instance.save()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=128, blank=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    address_line_1 = models.CharField(max_length=128)
    address_line_2 = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    zipcode = models.CharField(max_length=64)
    phone_number = models.CharField(default='', max_length=16,blank=True, null=True)
    description = models.TextField(blank=True)
    confirmed_age = models.BooleanField(default=False)


class Question(models.Model):
    name = models.CharField(max_length=64)
    email = models.EmailField()
    message = models.TextField(max_length=364)


class Visit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ip = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Support(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
