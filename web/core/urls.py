from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index')
]