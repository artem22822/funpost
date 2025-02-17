from django.urls import path
from . import views

app_name = 'agencies'

urlpatterns = [
    path('list', views.List.as_view(), name='list'),
    path('create', views.Create.as_view(), name='create'),
    path('<int:uuid>', views.Profile.as_view(), name='profile')

]
