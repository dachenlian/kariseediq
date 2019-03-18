from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('results', views.SearchResultsListView.as_view(), name='results'),
    path('create/', views.SenseCreateView.as_view(), name='create_sense'),
    path('update/<str:hw>/', views.SenseUpdateView.as_view(), name='update_headword'),
    path('update/<str:hw>/<int:sense>/', views.SenseUpdateView.as_view(), name='update_sense'),
    # path('entries/<int:pk>/delete/', views.EntryDeleteView.as_view(), name='delete'),
    path('entries/pending/', views.PendingListView.as_view(), name='pending'),
    path('export/<int:query_idx>/', views.export_search_to_csv, name='export'),
    # path('ajax/validate-item-name/', views.validate_item_name, name='validate_item_name'),
    path('ajax/root-autocomplete/', views.RootAutoComplete.as_view(), name='root_autocomplete'),
    path('ajax/root-sense-autocomplete/', views.RootSenseAutoComplete.as_view(), name='root_sense_autocomplete'),
    path('ajax/headword-autocomplete/', views.HeadwordAutoComplete.as_view(), name='headword_autocomplete')
]
