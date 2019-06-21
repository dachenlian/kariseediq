from django.urls import path
from . import views


app_name = 'freqdist'

urlpatterns = [
    path('upload/', views.TextFileUploadView.as_view(), name='upload'),
    path('<int:pk>/delete', views.TextSingleDeleteView.as_view(), name='single_delete'),
]
