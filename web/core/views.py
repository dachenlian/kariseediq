from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, FormView
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from core.models import Entry
from .forms import UpdateEntryForm


class IndexListView(ListView):
    model = Entry
    paginate_by = 100
    context_object_name = 'entries'
    template_name = 'core/index.html'
    ordering = ['-time']


class EntryUpdateView(UpdateView):
    form_class = UpdateEntryForm
    template_name = 'core/update.html'
    model = Entry

    # def get_initial(self):
    #     print(self.kwargs.get('pk'))
    #     entry = get_object_or_404(Entry, id=self.kwargs.get('pk'))
    #     initial = model_to_dict(entry)
    #     return initial


class SearchResultsListView(ListView):
    model = Entry
    paginate_by = 25
    context_object_name = 'entries'
    template_name = 'core/index.html'

    def get_queryset(self):
        item_filter = self.request.GET.get('itemFilter')
        item_name = self.request.GET.get('itemName')

        if item_filter == 'startswith':
            query = Entry.objects.filter(itemName__startswith=item_name)
        elif item_filter == 'endswith':
            query = Entry.objects.filter(itemName__endswith=item_name)
        else:
            query = Entry.objects.filter(itemName__contains=item_name)

        return query.order_by('-time')
