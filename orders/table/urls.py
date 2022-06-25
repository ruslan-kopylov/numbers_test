from django.urls import path
from .views import index

app_name = 'table'
urlpatterns = [
    path('', index, name='index'),
]