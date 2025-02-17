from django.contrib import admin
from django.urls import path, include
from engine.views import Login, Logout, Index, Register
from amazon.shipping import TrackShipping, CreateShipping
from engine.views import Profile, ProfileAddress, \
    RedirectToProfile, AddProducts, AddToCart, ProductCart, ProcessOrder, DeleteFromCart, CheckoutOrder, \
    PaidOrder, AllOrders, UpdateProductCart, SearchUsers, PageProduct, SupportMessageUser, SupportMessageAdmin, \
    DeleteProduct, EditProduct, SendTelegramShare
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', Index.as_view(), name='index'),

                  path('login/', Login.as_view(), name='login'),
                  path('logout/', Logout.as_view(), name='logout'),
                  path('sign-up/', Register.as_view(), name='signup'),
                  path('add-product/', AddProducts.as_view(), name='add-product'),

                  path('social-auth/', include('social_django.urls', namespace='social')),

                  path('orders/', AllOrders.as_view(), name='all-orders'),
                  path('search_users/', SearchUsers.as_view(), name='search-users'),

                  path('profile/address', ProfileAddress.as_view(), name='profile-address'),
                  path('redirect/', RedirectToProfile.as_view(), name='redirect_to_profile'),
                  path('profile/<str:username>', Profile.as_view(), name='profile'),
                  path('delete/<int:product_id>', DeleteProduct.as_view(), name='delete-product'),
                  path('edit/<str:product_uuid>', EditProduct.as_view(), name='edit-product'),

                  path('process/<str:order_uuid>', ProcessOrder.as_view(), name='process-order'),
                  path('checkout/<str:order_uuid>', CheckoutOrder.as_view(), name='checkout-order'),
                  path('paid/<str:order_uuid>', PaidOrder.as_view(), name='paid-order'),

                  path('profile/<str:username>/<str:product_uuid>', PageProduct.as_view(), name='page-product'),
                  # send telegram
                  path('send/telegram-share', SendTelegramShare.as_view(), name='send-telegram-share'),
                  path('send/telegram-register/social', SendTelegramShare.as_view(), name='send-telegram-share'),

                  # support
                  path('support/message/user', SupportMessageUser.as_view(), name='support-message-user'),
                  path('support/message/admin', SupportMessageAdmin.as_view(), name='support-message-admin'),

                  # api-amazon-shipping
                  path('api/create-shipping', CreateShipping.post, name='create-shipping'),
                  path('api/track-shipping', TrackShipping.get, name='track-shipping'),

                  # api order
                  path('api/add-to-cart', AddToCart.as_view(), name='add-to-cart'),
                  path('api/product-cart', ProductCart.as_view(), name='product-cart'),
                  path('api/delete-from-cart', DeleteFromCart.as_view(), name='delete-from-cart'),
                  path('api/update-product-cart', UpdateProductCart.as_view(), name='update-product-cart'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
