from django.urls import path, include
from . import views


app_name = 'freqdist'

urlpatterns = [
    path('upload/', views.TextFileUploadView.as_view(), name='upload'),
    path('<int:pk>/delete', views.TextSingleDeleteView.as_view(), name='delete_single'),
    path('delete-all/', views.TextAllDeleteView.as_view(), name='delete_all'),
    path('results/word-class', views.FreqResultsWordClassView.as_view(), name='results_word_class'),
    path('results/morpho', views.FreqResultsMorphoView.as_view(), name='results_morpho'),
    path('results/export', views.export_results_to_csv, name='export'),
]
