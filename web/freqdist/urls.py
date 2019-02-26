from django.urls import path
from . import views


app_name = 'freqdist'

urlpatterns = [
    path('upload/', views.TextFileUploadView.as_view(), name='upload'),
]
