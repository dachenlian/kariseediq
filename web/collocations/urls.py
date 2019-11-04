from django.urls import path
from .views import CollocationView

app_name = 'collocations'

urlpatterns = [
    path('', CollocationView.as_view(), name='index'),
]