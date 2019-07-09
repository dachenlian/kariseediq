from django.urls import path

from kwic import views

app_name = 'kwic'

urlpatterns = [
    path('', views.KwicView.as_view(), name='index'),
]
