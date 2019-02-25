from django.urls import path
from . import views


urlpatterns = [
    path('upload/', views.TextFileUploadView.as_view(), name='upload'),
]
