from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('results', views.SearchResultsListView.as_view(), name='results'),
    path('create/', views.EntryCreateView.as_view(), name='create'),
    path('entries/<int:pk>', views.EntryExampleUpdateView.as_view(), name='update'),
    path('export/', views.export_search_to_csv, name='export'),
    path('ajax/validate_item_name', views.validate_item_name, name='validate_item_name'),
]
