from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('results', views.SearchResultsListView.as_view(), name='results'),
    path('entries/<int:pk>', views.EntryUpdateView.as_view(), name='update'),

]
