from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    # path('results', views.SearchResultsListView.as_view(), name='results'),
    # path('create/', views.EntryCreateView.as_view(), name='create'),
    path('update/<str:hw>/<int:sense>/', views.SenseUpdateView.as_view(), name='update'),
    # path('entries/<int:pk>/delete/', views.EntryDeleteView.as_view(), name='delete'),
    # path('entries/pending/', views.EntryPendingListView.as_view(), name='pending'),
    # path('export/<int:query_idx>/', views.export_search_to_csv, name='export'),
    # path('ajax/validate-item-name/', views.validate_item_name, name='validate_item_name'),
    # path('ajax/focus-autocomplete/', views.EntryRootAutoComplete.as_view(), name='focus_autocomplete'),
    # path('ajax/item-name-autocomplete/', views.EntryItemNameAutoComplete.as_view(), name='item_name_autocomplete')
]
