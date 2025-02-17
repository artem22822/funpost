from django.urls import path
from . import views

app_name = 'package'

urlpatterns = [
    path('list', views.List.as_view(), name='list'),
    path('create', views.Request.as_view(), name='create'),
    path('', views.RequestUpdate.as_view(), name='request'),

]
